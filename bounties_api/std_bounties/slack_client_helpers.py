from decimal import Decimal
from std_bounties.client_helpers import calculate_token_quantity
from bounties.utils import bounty_url_for
from utils.functional_tools import narrower


def notify_slack(sc, channel, event, msg):
    sc.api_call(
        'chat.postMessage',
        channel=channel,
        text='*{}*: {}'.format(event, msg),
        mrkdwn=True
    )

    return True


def format_message(fields, msg_string, **kwargs):
    return msg_string.format(**{**fields, **kwargs})


def get_base_bounty_values(bounty):
    base_fields = narrower(
        bounty,
        [
            'title',
            'bounty_id',
            'token_symbol',
            'token_decimals'
        ]
    )

    base_fields['total_value'] = calculate_token_quantity(bounty.fulfillment_amount, bounty.token_decimals)
    base_fields['usd_price'] = Decimal(bounty.usd_price).quantize(Decimal(10) ** -2)
    base_fields['deadline'] = bounty.deadline.strftime('%m/%d/%Y')
    base_fields['token_price'] = 'Unkown Price' if not bounty.token else Decimal(bounty.token.price_usd).quantize(Decimal(10) ** -2)
    base_fields['token_lock_price'] = 'Unkown Price' if not bounty.token_lock_price else Decimal(bounty.token_lock_price).quantize(Decimal(10) ** -2)
    base_fields['link'] = bounty_url_for(bounty.bounty_id, bounty.platform)

    return base_fields
