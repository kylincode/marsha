"""Admin of the ``core`` app of the Marsha project."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from safedelete.admin import SafeDeleteAdmin

from marsha.core.models import (
    AudioTrack,
    ConsumerSite,
    ConsumerSiteAccess,
    ConsumerSiteOrganization,
    Organization,
    OrganizationAccess,
    Playlist,
    PlaylistAccess,
    SignTrack,
    SubtitleTrack,
    User,
    Video,
)


class MarshaAdminSite(admin.AdminSite):
    """Admin site for Marsha."""

    site_title = _("{marsha_name} administration").format(marsha_name="Marsha")
    site_header = "Marsha"


admin_site = MarshaAdminSite(name="admin")


class BaseModelAdmin(SafeDeleteAdmin):
    """Base for all our model admins."""

    pass


class UserOrganizationsInline(admin.TabularInline):
    """Inline to display organizations to which a user has been granted access."""

    model = OrganizationAccess
    verbose_name = _("organization")
    verbose_name_plural = _("organizations")


@admin.register(User, site=admin_site)
class UserAdmin(DefaultUserAdmin):
    """Admin class for the User model."""

    inlines = DefaultUserAdmin.inlines + [UserOrganizationsInline]


class ConsumerSiteUsersInline(admin.TabularInline):
    """Inline to display users who have been granted access to a consumer site."""

    model = ConsumerSiteAccess
    verbose_name = _("user")
    verbose_name_plural = _("users")


class ConsumerSiteOrganizationsInline(admin.TabularInline):
    """Inline to display organizations for a consumer site."""

    model = ConsumerSiteOrganization
    verbose_name = _("organization")
    verbose_name_plural = _("organizations")


@admin.register(ConsumerSite, site=admin_site)
class ConsumerSiteAdmin(BaseModelAdmin):
    """Admin class for the ConsumerSite model."""

    list_display = ("name",)
    inlines = [ConsumerSiteUsersInline, ConsumerSiteOrganizationsInline]


class OrganizationUsersInline(admin.TabularInline):
    """Inline to display users who have been granted access to an organization."""

    model = OrganizationAccess
    verbose_name = _("user")
    verbose_name_plural = _("users")


class OrganizationConsumerSitesInline(admin.TabularInline):
    """Inline to display consumer sites for an organization."""

    model = ConsumerSiteOrganization
    verbose_name = _("consumer site")
    verbose_name_plural = _("consumer sites")


@admin.register(Organization, site=admin_site)
class OrganizationAdmin(BaseModelAdmin):
    """Admin class for the Organization model."""

    list_display = ("name",)
    inlines = [OrganizationUsersInline, OrganizationConsumerSitesInline]


class AudioTrackInline(admin.TabularInline):
    """Inline for audio tracks of a video."""

    model = AudioTrack


class SubtitleTrackInline(admin.TabularInline):
    """Inline for subtitle tracks of a video."""

    model = SubtitleTrack


class SignTrackInline(admin.TabularInline):
    """Inline for sign tracks of a video."""

    model = SignTrack


@admin.register(Video, site=admin_site)
class VideoAdmin(BaseModelAdmin):
    """Admin class for the Video model."""

    list_display = ("title", "created_by", "language")
    exclude = ("duplicated_from",)
    inlines = [AudioTrackInline, SubtitleTrackInline, SignTrackInline]


class VideosInline(admin.TabularInline):
    """Inline for videos in a playlist."""

    model = Video
    verbose_name = _("video")
    verbose_name_plural = _("videos")


class PlaylistAccessesInline(admin.TabularInline):
    """Inline for with right to write access to a playlist."""

    model = PlaylistAccess
    verbose_name = _("user access")
    verbose_name_plural = _("users accesses")


@admin.register(Playlist, site=admin_site)
class PlaylistAdmin(BaseModelAdmin):
    """Admin class for the Playlist model."""

    list_display = ("title", "organization", "created_by", "is_public")
    exclude = ("duplicated_from",)
    inlines = [VideosInline, PlaylistAccessesInline]
