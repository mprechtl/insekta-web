import binascii
import datetime

from cryptography.hazmat.primitives import hashes
from django.db import models
from django.conf import settings
import pytz

from .certs import CSRSigner, SignError, pem_to_cert, cert_to_pem


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    pem_data = models.TextField()
    fingerprint = models.CharField(max_length=64, unique=True)
    expires = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    def __str__(self):
        return 'Certificate {} for {}'.format(self.fingerprint, self.user)

    def get_x509_certificate(self):
        if not hasattr(self, '_x509_certificate'):
            self._x509_certificate = pem_to_cert(self.pem_data)
        return self._x509_certificate

    def set_x509_certificate(self, cert):
        self._x509_certificate = cert
        self._update_fields(cert)

    @property
    def is_expired(self):
        return self.expires < datetime.datetime.now(pytz.UTC)

    @property
    def is_valid(self):
        return not self.is_revoked and not self.is_expired

    def revoke(self):
        self.is_revoked = True
        self.save()
        # TODO: Put to CSRL

    @classmethod
    def create_from_csr(cls, user, csr_pem):
        """Creates a Certificate object for a user using a CSR.

        :param user: User for which the certificate should be issued
        :param csr_pem: PEM-encoded Certificate Signing Request
        :raises: SignError
        :return: Certificate
        """
        signer = CSRSigner(settings.CA_PRIVATE_KEYFILE, settings.CA_CN)
        x509_cert = signer.sign_csr(csr_pem, user.username)
        cert = cls(user=user)
        cert.set_x509_certificate(x509_cert)
        cert.save()
        return cert

    def _update_fields(self, cert):
        self.pem_data = cert_to_pem(cert)
        self.expires = cert.not_valid_after
        fingerprint = binascii.hexlify(cert.fingerprint(hashes.SHA256()))
        self.fingerprint = fingerprint.decode()
