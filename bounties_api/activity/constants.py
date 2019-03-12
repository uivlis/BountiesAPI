DRAFT_CREATED = 'DCR'
DRAFT_UPDATED = 'DUP'

BOUNTY_ISSUED = 'BIS'
BOUNTY_ACTIVATED = 'BAC'
BOUNTY_EXPIRED = 'BEX'
BOUNTY_KILLED = 'BKI'
BOUNTY_COMPLETED = 'BCO'

BOUNTY_CONTRIBUTION_ADDED = 'BCA'
BOUNTY_DEADLINE_EXTENDED = 'BDE'
BOUNTY_TRANSFERRED = 'BTR'
BOUNTY_PAYOUT_INCREASED = 'BPI'
BOUNTY_COMMENT_CREATED = 'BCC'

FULFILLMENT_CREATED = 'FCR'
FULFILLMENT_ACCEPTED = 'FAC'

USER_PROFILE_UPDATED = 'UPU'
USER_RATING_ISSUED = 'URI'
USER_JOINED_GROUP = 'UJG'
USER_LEFT_GROUP = 'ULG'


ACTIVITY_TYPES = (
    (DRAFT_CREATED, 'DRAFT_CREATED'),
    (DRAFT_UPDATED, 'DRAFT_UPDATED'),

    (BOUNTY_ISSUED, 'BOUNTY_ISSUED'),
    (BOUNTY_ACTIVATED, 'BOUNTY_ACTIVATED'),
    (BOUNTY_EXPIRED, 'BOUNTY_EXPIRED'),
    (BOUNTY_KILLED, 'BOUNTY_KILLED'),
    (BOUNTY_COMPLETED, 'BOUNTY_COMPLETED'),

    (BOUNTY_CONTRIBUTION_ADDED, 'BOUNTY_CONTRIBUTION_ADDED'),
    (BOUNTY_DEADLINE_EXTENDED, 'BOUNTY_DEADLINE_EXTENDED'),
    (BOUNTY_TRANSFERRED, 'BOUNTY_TRANSFERRED'),
    (BOUNTY_PAYOUT_INCREASED, 'BOUNTY_PAYOUT_INCREASED'),
    (BOUNTY_COMMENT_CREATED, 'BOUNTY_COMMENT_CREATED'),

    (FULFILLMENT_CREATED, 'FULFILLMENT_CREATED'),
    (FULFILLMENT_ACCEPTED, 'FULFILLMENT_ACCEPTED'),

    (USER_PROFILE_UPDATED, 'USER_PROFILE_UPDATED'),
    (USER_RATING_ISSUED, 'USER_RATING_ISSUED'),
    (USER_JOINED_GROUP, 'USER_JOINED_GROUP'),
    (USER_LEFT_GROUP, 'USER_LEFT_GROUP'),
)

id_to_activity = dict(ACTIVITY_TYPES)
activity_to_id = dict((y, x) for x, y in id_to_activity.items())