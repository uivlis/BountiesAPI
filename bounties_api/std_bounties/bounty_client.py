import datetime
from decimal import Decimal
from std_bounties.models import Fulfillment, DraftBounty
from std_bounties.serializers import BountySerializer, FulfillmentSerializer
from std_bounties.constants import DRAFT_STAGE, ACTIVE_STAGE, DEAD_STAGE, COMPLETED_STAGE, EXPIRED_STAGE
from std_bounties.client_helpers import map_bounty_data, map_token_data, map_fulfillment_data, get_token_pricing, \
    get_historic_pricing, map_token_data_v2
from bounties.utils import getDateTimeFromTimestamp
from django.db import transaction
import logging

logger = logging.getLogger('django')

issue_bounty_input_keys = [
    'fulfillmentAmount',
    'arbiter',
    'paysTokens',
    'tokenContract',
    'value']
issue_bounty_input_keys_v2 = [
    'approvers',
    'tokenVersion',
    'token']


class BountyClient:

    def __init__(self):
        pass

    @transaction.atomic
    def issue_bounty(self, bounty_id, inputs, event_timestamp, **kwargs):
        data_hash = inputs.get('data', 'invalid')
        original_bounty_id = kwargs.get('original_id', bounty_id)
        contract_version = kwargs.get('contract_version', 1)
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        ipfs_data = map_bounty_data(data_hash, bounty_id)

        if contract_version == 1:
            token_data = map_token_data(
                inputs.get('paysTokens'),
                inputs.get('tokenContract'),
                inputs.get('fulfillmentAmount'))
            bounty_data = {
                'id': bounty_id,
                'bounty_id': original_bounty_id,
                'issuer': inputs.get('issuer', '').lower(),
                'deadline': getDateTimeFromTimestamp(inputs.get('deadline', None)),
                'bountyStage': DRAFT_STAGE,
                'bounty_created': event_date,
            }
            plucked_inputs = {key: inputs.get(key)
                              for key in issue_bounty_input_keys}

        elif contract_version == 2:
            token_data = map_token_data_v2(inputs.get('tokenVersion'), inputs.get('token'), 0)
            bounty_data = {
                'id': bounty_id,
                'bounty_id': original_bounty_id,
                'issuers': inputs.get('issuers', []),
                'deadline': getDateTimeFromTimestamp(inputs.get('deadline', None)),
                'bounty_created': event_date,
                'bountyStage': ACTIVE_STAGE,
                'fulfillmentAmount': 0,
                'issuer': inputs.get('issuers', [])[0],
                'paysTokens': inputs.get('tokenVersion') != 0
            }
            plucked_inputs = {key: inputs.get(key)
                              for key in issue_bounty_input_keys_v2}

        bounty_serializer = BountySerializer(
            data={
                **bounty_data,
                **plucked_inputs,
                **ipfs_data,
                **token_data})
        bounty_serializer.is_valid(raise_exception=True)
        saved_bounty = bounty_serializer.save()
        saved_bounty.save_and_clear_categories(
            ipfs_data.get('data_categories'))
        saved_bounty.record_bounty_state(event_date)
        uid = saved_bounty.uid
        if uid:
            DraftBounty.objects.filter(uid=uid).update(on_chain=True)
        return saved_bounty

    def activate_bounty(self, bounty, inputs, event_timestamp, **kwargs):
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        bounty.bountyStage = ACTIVE_STAGE
        bounty.record_bounty_state(event_date)
        bounty.save()

        return bounty

    def fulfill_bounty(
            self,
            bounty,
            fulfillment_id,
            inputs,
            event_timestamp,
            transaction_issuer,
            **kwargs):

        fulfillment = Fulfillment.objects.filter(
            fulfillment_id=fulfillment_id, bounty_id=bounty.bounty_id
        )

        if fulfillment.exists():
            return

        data_hash = inputs.get('data')
        ipfs_data = map_fulfillment_data(
            data_hash, bounty.bounty_id, fulfillment_id)

        fulfillment_data = {
            'fulfillment_id': fulfillment_id,
            'fulfiller': transaction_issuer.lower(),
            'bounty': bounty.bounty_id,
            'accepted': False,
            'fulfillment_created': datetime.datetime.fromtimestamp(
                int(event_timestamp)),
        }

        fulfillment_serializer = FulfillmentSerializer(
            data={**fulfillment_data, **ipfs_data})
        fulfillment_serializer.is_valid(raise_exception=True)
        instance = fulfillment_serializer.save()

        return instance

    def update_fulfillment(self, bounty, fulfillment_id, inputs, **kwargs):
        fulfillment = Fulfillment.objects.get(
            fulfillment_id=fulfillment_id, bounty_id=bounty.bounty_id)

        data_hash = inputs.get('data')
        ipfs_data = map_fulfillment_data(
            data_hash, bounty.bounty_id, fulfillment_id)

        fulfillment_serializer = FulfillmentSerializer(
            fulfillment, data={**ipfs_data}, partial=True)
        instance = fulfillment_serializer.save()

        return instance

    @transaction.atomic
    def accept_fulfillment(
            self,
            bounty,
            fulfillment_id,
            event_timestamp,
            **kwargs):
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        bounty.balance = bounty.balance - bounty.fulfillmentAmount
        usd_price, token_price = get_historic_pricing(
            bounty.tokenSymbol,
            bounty.tokenDecimals,
            bounty.fulfillmentAmount,
            event_timestamp)

        if bounty.balance < bounty.fulfillmentAmount:
            bounty.bountyStage = COMPLETED_STAGE
            bounty.usd_price = usd_price
            bounty.tokenLockPrice = token_price
            bounty.record_bounty_state(event_date)
        bounty.save()

        fulfillment = Fulfillment.objects.get(
            bounty_id=bounty.bounty_id, fulfillment_id=fulfillment_id)
        fulfillment.accepted = True
        fulfillment.usd_price = usd_price
        fulfillment.accepted_date = getDateTimeFromTimestamp(event_timestamp)
        fulfillment.save()

        return fulfillment

    def kill_bounty(self, bounty, event_timestamp, **kwargs):
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        bounty.old_balance = bounty.balance
        bounty.balance = 0
        usd_price, token_price = get_historic_pricing(
            bounty.tokenSymbol,
            bounty.tokenDecimals,
            bounty.fulfillmentAmount,
            event_timestamp)
        has_accepted_fulfillments = bounty.fulfillments.filter(
            accepted=True).exists()
        if has_accepted_fulfillments:
            bounty.bountyStage = COMPLETED_STAGE
        else:
            bounty.bountyStage = DEAD_STAGE
        bounty.usd_price = usd_price
        bounty.tokenLockPrice = token_price
        bounty.record_bounty_state(event_date)
        bounty.save()

        return bounty

    def add_contribution(self, bounty, inputs, event_timestamp, **kwargs):
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        bounty.balance = Decimal(bounty.balance) + Decimal(inputs.get('value'))
        if bounty.balance >= bounty.fulfillmentAmount and bounty.bountyStage == EXPIRED_STAGE:
            bounty.bountyStage = ACTIVE_STAGE
            bounty.record_bounty_state(event_date)
        if bounty.balance >= bounty.fulfillmentAmount and bounty.bountyStage == COMPLETED_STAGE:
            bounty.bountyStage = ACTIVE_STAGE
            bounty.record_bounty_state(event_date)
            usd_price = get_token_pricing(
                bounty.tokenSymbol,
                bounty.tokenDecimals,
                bounty.fulfillmentAmount)[0]
            bounty.usd_price = usd_price
        bounty.save()

        return bounty

    def extend_deadline(self, bounty, inputs, event_timestamp, **kwargs):
        event_date = datetime.datetime.fromtimestamp(int(event_timestamp))
        bounty.deadline = getDateTimeFromTimestamp(
            inputs.get('newDeadline', None))
        if bounty.deadline > datetime.datetime.now(
        ) and bounty.bountyStage == EXPIRED_STAGE:
            bounty.bountyStage = ACTIVE_STAGE
            bounty.record_bounty_state(event_date)
        bounty.save()

        return bounty

    @transaction.atomic
    def change_bounty(self, bounty, inputs, **kwargs):
        updated_data = {}
        data_hash = inputs.get('newData', None) or inputs.get('data', None)
        deadline = inputs.get('newDeadline', None)
        fulfillmentAmount = inputs.get('newFulfillmentAmount', None)
        arbiter = inputs.get('newArbiter', None)

        if data_hash:
            updated_data = map_bounty_data(data_hash, bounty.bounty_id)

        if deadline:
            updated_data['deadline'] = datetime.datetime.fromtimestamp(
                int(deadline))

        if fulfillmentAmount:
            updated_data['fulfillmentAmount'] = Decimal(fulfillmentAmount)

        if arbiter:
            updated_data['arbiter'] = arbiter

        bounty_serializer = BountySerializer(
            bounty, data=updated_data, partial=True)
        bounty_serializer.is_valid(raise_exception=True)
        saved_bounty = bounty_serializer.save()

        if data_hash:
            saved_bounty.save_and_clear_categories(
                updated_data.get('data_categories'))

        if fulfillmentAmount:
            usd_price = get_token_pricing(
                saved_bounty.tokenSymbol,
                saved_bounty.tokenDecimals,
                fulfillmentAmount)[0]
            saved_bounty.usd_price = usd_price
            saved_bounty.save()

        return saved_bounty

    def transfer_issuer(self, bounty, inputs, **kwargs):
        bounty.issuer = inputs.get('newIssuer')
        bounty.save()

        return bounty

    def increase_payout(self, bounty, inputs, **kwargs):
        value = inputs.get('value')
        fulfillment_amount = inputs.get('newFulfillmentAmount')
        if value:
            bounty.balance = bounty.balance + Decimal(value)
        usd_price = get_token_pricing(
            bounty.tokenSymbol,
            bounty.tokenDecimals,
            fulfillment_amount)[0]
        bounty.fulfillmentAmount = Decimal(fulfillment_amount)
        bounty.usd_price = usd_price
        bounty.save()

        return bounty
