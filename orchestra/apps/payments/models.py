from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import accounts

from . import settings
from .methods import PaymentMethod


class PaymentSource(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='payment_sources')
    method = models.CharField(_("method"), max_length=32,
            choices=PaymentMethod.get_plugin_choices())
    data = JSONField(_("data"))
    is_active = models.BooleanField(_("is active"), default=True)
    
    def __unicode__(self):
        return self.label or str(self.account)
    
    @cached_property
    def label(self):
        try:
            plugin = PaymentMethod.get_plugin(self.method)()
        except KeyError:
            return None
        return plugin.get_label(self.data)
    
    @cached_property
    def number(self):
        try:
            plugin = PaymentMethod.get_plugin(self.method)()
        except KeyError:
            return None
        return plugin.get_number(self.data)


# TODO lock transaction in waiting confirmation
class Transaction(models.Model):
    WAITTING_PROCESSING = 'WAITTING_PROCESSING'
    WAITTING_CONFIRMATION = 'WAITTING_CONFIRMATION'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    LOCKED = 'LOCKED'
    DISCARTED = 'DISCARTED'
    STATES = (
        (WAITTING_PROCESSING, _("Waitting processing")),
        (WAITTING_CONFIRMATION, _("Waitting confirmation")),
        (CONFIRMED, _("Confirmed")),
        (REJECTED, _("Rejected")),
        (LOCKED, _("Locked")),
        (DISCARTED, _("Discarted")),
    )
    
    # TODO account fk?
    bill = models.ForeignKey('bills.bill', verbose_name=_("bill"),
            related_name='transactions')
    source = models.ForeignKey(PaymentSource, null=True, blank=True,
            verbose_name=_("source"), related_name='transactions')
    state = models.CharField(_("state"), max_length=32, choices=STATES,
            default=WAITTING_PROCESSING)
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=settings.PAYMENT_CURRENCY)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    related = models.ForeignKey('self', null=True, blank=True)
    
    def __unicode__(self):
        return "Transaction {}".format(self.id)


# TODO rename to TransactionProcess or PaymentRequest TransactionRequest
class PaymentProcess(models.Model):
    """
    Stores arbitrary data generated by payment methods while processing transactions
    """
    transactions = models.ManyToManyField(Transaction, related_name='processes',
            verbose_name=_("transactions"))
    data = JSONField(_("data"), blank=True)
    file = models.FileField(_("file"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    
    # TODO state: created, commited, secured (delayed persistence)
    
    def __unicode__(self):
        return str(self.id)


accounts.register(PaymentSource)
accounts.register(Transaction)
