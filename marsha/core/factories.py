"""Factories for the ``core`` app of the Marsha project."""
from django.contrib.auth.hashers import make_password
from django.utils import timezone

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from marsha.core import models


class PlaylistLTIPassportFactory(DjangoModelFactory):
    """Factory to create LTI passport for a playlist."""

    class Meta:  # noqa
        model = models.LTIPassport

    playlist = factory.SubFactory("marsha.core.factories.PlaylistFactory")


class ConsumerSiteLTIPassportFactory(DjangoModelFactory):
    """Factory to create LTI passport for a consumer site."""

    class Meta:  # noqa
        model = models.LTIPassport

    consumer_site = factory.SubFactory("marsha.core.factories.ConsumerSiteFactory")


class UserFactory(DjangoModelFactory):
    """Factory for the User model."""

    class Meta:  # noqa
        model = models.User

    username = factory.Faker("user_name")
    password = make_password(u"password")


class ConsumerSiteFactory(DjangoModelFactory):
    """Factory for the ConsumerSite model."""

    class Meta:  # noqa
        model = models.ConsumerSite

    name = factory.Sequence("Site {:03d}".format)


class ConsumerSiteAccessFactory(DjangoModelFactory):
    """Factory for the ConsumerSiteAccess model."""

    class Meta:  # noqa
        model = models.ConsumerSiteAccess


class OrganizationFactory(DjangoModelFactory):
    """Factory for the Organization model."""

    class Meta:  # noqa
        model = models.Organization

    name = factory.Faker("company")


class ConsumerSiteOrganizationFactory(DjangoModelFactory):
    """Factory for the SiteOrganization model."""

    class Meta:  # noqa
        model = models.ConsumerSiteOrganization


class OrganizationAccessFactory(DjangoModelFactory):
    """Factory for the OrganizationAccess model."""

    class Meta:  # noqa
        model = models.OrganizationAccess


class PlaylistFactory(DjangoModelFactory):
    """Factory for the Playlist model."""

    class Meta:  # noqa
        model = models.Playlist

    title = factory.Sequence("Playlist {:03d}".format)
    consumer_site = factory.SubFactory(ConsumerSiteFactory)
    lti_id = factory.Sequence("playlist#{:d}".format)


class PlaylistAccessFactory(DjangoModelFactory):
    """Factory for the PlaylistAccess model."""

    class Meta:  # noqa
        model = models.PlaylistAccess


class VideoFactory(DjangoModelFactory):
    """Factory for the Video model."""

    class Meta:  # noqa
        model = models.Video

    title = factory.Sequence("Video {:03d}".format)
    description = factory.Faker("catch_phrase")
    position = fuzzy.FuzzyInteger(0)
    playlist = factory.SubFactory(PlaylistFactory)
    lti_id = factory.Sequence("video#{:d}".format)
    uploaded_on = fuzzy.FuzzyDateTime(timezone.now())


class AudioTrackFactory(DjangoModelFactory):
    """Factory for the AudioTrack model."""

    class Meta:  # noqa
        model = models.AudioTrack


class SubtitleTrackFactory(DjangoModelFactory):
    """Factory for the SubtitleTrack model."""

    class Meta:  # noqa
        model = models.SubtitleTrack


class SignTrackFactory(DjangoModelFactory):
    """Factory for the SignTrack model."""

    class Meta:  # noqa
        model = models.SignTrack
