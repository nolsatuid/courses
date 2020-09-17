from django.shortcuts import redirect

from fortuna_client.callback import RemoteTransactionCallback
from fortuna_client.transaction import RemoteTransaction

from nolsatu_courses.apps.products.models import Order


class FortunaCallback(RemoteTransactionCallback):
    def on_callback(self, transaction: RemoteTransaction):
        remote_status_map = {
            RemoteTransaction.Status.CREATED: Order.STATUS.created,
            RemoteTransaction.Status.SUCCESS: Order.STATUS.success,
            RemoteTransaction.Status.PENDING: Order.STATUS.pending,
            RemoteTransaction.Status.FAILED: Order.STATUS.failed,
            RemoteTransaction.Status.EXPIRED: Order.STATUS.expired,
            RemoteTransaction.Status.REFUND: Order.STATUS.other,
            RemoteTransaction.Status.OTHER: Order.STATUS.created,
        }

        current_order = Order.objects.filter(remote_transaction_id=transaction.id).first()

        if not current_order:
            return

        if current_order.status != Order.STATUS.pending:
            return

        current_order.status = remote_status_map[transaction.status]
        current_order.save()
        # TODO: Send Confirmation Email / Message

    def payment_redirect(self, request, transaction_id):
        # TODO: Update when transaction detail is ready
        return redirect("website:index")
