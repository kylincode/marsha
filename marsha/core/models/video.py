"""This module holds the models for the marsha project."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from safedelete import HARD_DELETE

from ..utils.time_utils import to_timestamp
from .account import INSTRUCTOR, ROLE_CHOICES
from .base import BaseModel, NonDeletedUniqueIndex


class Playlist(BaseModel):
    """Model representing a playlist which is a list of videos."""

    title = models.CharField(
        max_length=255, verbose_name=_("title"), help_text=_("title of the playlist")
    )
    lti_id = models.CharField(
        max_length=255,
        verbose_name=_("lti id"),
        help_text=_("ID for synchronization with an external LTI tool"),
    )
    organization = models.ForeignKey(
        to="Organization",
        related_name="playlists",
        # playlist is (soft-)deleted if organization is (soft-)deleted
        on_delete=models.CASCADE,
        null=True,
    )
    consumer_site = models.ForeignKey(
        to="ConsumerSite",
        related_name="playlists",
        # playlist is (soft-)deleted if organization is (soft-)deleted
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        to="User",
        related_name="created_playlists",
        # playlist is (soft-)deleted if author is (soft-)deleted
        on_delete=models.CASCADE,
        null=True,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("is public"),
        help_text=_("if this playlist can be viewed without any access control"),
    )
    duplicated_from = models.ForeignKey(
        to="self",
        related_name="duplicates",
        verbose_name=_("duplicate from"),
        help_text=_("original playlist this one was duplicated from"),
        # don't delete a playlist if the one it was duplicated from is hard deleted
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    users = models.ManyToManyField(
        to="User",
        through="PlaylistAccess",
        related_name="playlists",
        verbose_name=_("users"),
        help_text=_("users who have been granted access to this playlist"),
    )

    class Meta:
        """Options for the ``Playlist`` model."""

        db_table = "playlist"
        verbose_name = _("playlist")
        verbose_name_plural = _("playlists")


class PlaylistAccess(BaseModel):
    """
    Model representing accesses to playlists that are granted to users.

    ``through`` model between ``Playlist.users`` and ``User.playlists``.

    """

    # we allow deleting entries in this through table
    _safedelete_policy = HARD_DELETE

    user = models.ForeignKey(
        to="User",
        related_name="playlist_accesses",
        verbose_name=_("user"),
        help_text=_("user who has access to the playlist"),
        # link is (soft-)deleted if user is (soft-)deleted
        on_delete=models.CASCADE,
    )
    playlist = models.ForeignKey(
        to="Playlist",
        related_name="user_accesses",
        verbose_name=_("playlist"),
        help_text=_("playlist to which the user has access"),
        # link is (soft-)deleted if playlist is (soft-)deleted
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name=_("role"),
        help_text=_("role granted to the user on the consumer site"),
        default=INSTRUCTOR,
    )

    class Meta:
        """Options for the ``PlaylistAccess`` model."""

        db_table = "playlist_access"
        verbose_name = _("playlist access")
        verbose_name_plural = _("playlist accesses")
        indexes = [NonDeletedUniqueIndex(["user", "playlist"])]


class Video(BaseModel):
    """Model representing a video, created by an author."""

    PENDING, ERROR, READY = "pending", "error", "ready"
    STATE_CHOICES = ((PENDING, _("pending")), (ERROR, _("error")), (READY, _("ready")))

    title = models.CharField(
        max_length=255, verbose_name=_("title"), help_text=_("title of the video")
    )
    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("description of the video"),
        blank=True,
        null=True,
    )
    lti_id = models.CharField(
        max_length=255,
        verbose_name=_("lti id"),
        help_text=_("ID for synchronization with an external LTI tool"),
    )
    created_by = models.ForeignKey(
        to="User",
        related_name="created_videos",
        verbose_name=_("author"),
        help_text=_("author of the video"),
        # video is (soft-)deleted if author is (soft-)deleted
        on_delete=models.CASCADE,
        null=True,
    )
    language = models.CharField(
        max_length=5,
        choices=settings.LANGUAGES,
        verbose_name=_("language"),
        help_text=_("language of the video"),
    )
    playlist = models.ForeignKey(
        to="Playlist",
        related_name="videos",
        verbose_name=_("playlist"),
        help_text=_("playlist to which this video belongs"),
        # don't allow hard deleting a playlist if it still contains videos
        on_delete=models.PROTECT,
    )
    position = models.PositiveIntegerField(
        verbose_name=_("position"),
        help_text=_("position of this video in the playlist"),
        default=0,
    )
    duplicated_from = models.ForeignKey(
        to="self",
        related_name="duplicates",
        verbose_name=_("duplicate from"),
        help_text=_("original video this one was duplicated from"),
        # don't delete a video if the one it was duplicated from is hard deleted
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_on = models.DateTimeField(
        verbose_name=_("uploaded on"),
        help_text=_("datetime at which the active version of the video was uploaded."),
        null=True,
        blank=True,
    )
    state = models.CharField(
        max_length=20,
        verbose_name=_("state"),
        help_text=_("state of the upload and transcoding pipeline in AWS."),
        choices=STATE_CHOICES,
        default=PENDING,
    )

    class Meta:
        """Options for the ``Video`` model."""

        db_table = "video"
        ordering = ["position", "id"]
        verbose_name = _("video")
        verbose_name_plural = _("videos")

    def __str__(self):
        """Get the string representation of an instance."""
        result = f"{self.title}"
        if self.deleted:
            result += _(" [deleted]")
        return result

    def get_source_s3_key(self, stamp=None):
        """Compute the S3 key in the source bucket (ID of the playlist/ID of the video).

        Parameters
        ----------
        stamp: Type[string]
            Passing a value for this argument will return the source S3 key for the video assuming
            its active stamp is set to this value. This is useful to create an upload policy for
            this prospective version of the video, so that the client can upload the file to S3
            and the confirmation lambda can set the `uploaded_on` field to this value only after
            the video transcoding job is successful.

        Returns
        -------
        string
            The S3 key for the video in the source bucket, where uploaded videos are stored before
            they are converted to the destination bucket.

        """
        stamp = stamp or self.active_stamp
        return "{playlist!s}/{video!s}/videos/{stamp:s}".format(
            playlist=self.playlist.id, video=self.id, stamp=stamp
        )

    @property
    def active_stamp(self):
        """Return the current valid datetime of upload as a timestamp."""
        return str(to_timestamp(self.uploaded_on)) if self.uploaded_on else None


class BaseTrack(BaseModel):
    """Base model for different kinds of tracks tied to a video."""

    video = models.ForeignKey(
        to="Video",
        related_name="%(class)ss",  # will be `audiotracks` for `AudioTrack` model,
        verbose_name=_("video"),
        help_text=_("video for which this track is"),
        # track is (soft-)deleted if video is (soft-)deleted
        on_delete=models.CASCADE,
    )
    language = models.CharField(
        max_length=5,
        choices=settings.LANGUAGES,
        verbose_name=_("track language"),
        help_text=_("language of this track"),
    )

    class Meta:
        """Options for the ``BaseTrack`` model."""

        abstract = True


class AudioTrack(BaseTrack):
    """Model representing an additional audio track for a video."""

    class Meta:
        """Options for the ``AudioTrack`` model."""

        db_table = "audio_track"
        verbose_name = _("audio track")
        verbose_name_plural = _("audio tracks")
        indexes = [NonDeletedUniqueIndex(["video", "language"])]


class SubtitleTrack(BaseTrack):
    """Model representing a subtitle track for a video."""

    has_closed_captioning = models.BooleanField(
        default=False,
        verbose_name=_("closed captioning"),
        help_text=_(
            "if closed captioning (for deaf or hard of hearing viewers) "
            "is on for this subtitle track"
        ),
    )

    class Meta:
        """Options for the ``SubtitleTrack`` model."""

        db_table = "subtitle_track"
        verbose_name = _("subtitles track")
        verbose_name_plural = _("subtitles tracks")
        indexes = [
            NonDeletedUniqueIndex(["video", "language", "has_closed_captioning"])
        ]


class SignTrack(BaseTrack):
    """Model representing a signs language track for a video."""

    class Meta:
        """Options for the ``SignTrack`` model."""

        db_table = "sign_track"
        verbose_name = _("signs language track")
        verbose_name_plural = _("signs language tracks")
        indexes = [NonDeletedUniqueIndex(["video", "language"])]
