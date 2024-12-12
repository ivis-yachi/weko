# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.


"""Database models for weko-admin."""

from datetime import datetime
import enum
import traceback
from typing import List

from flask import current_app
from invenio_db import db
from sqlalchemy import CheckConstraint, desc, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import INET, INTERVAL
from sqlalchemy.sql.functions import concat ,now
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import JSONType

from weko_records.models import ItemType

""" PDF cover page model"""


class PDFCoverPageSettings(db.Model):
    """PDF Cover Page Settings."""

    __tablename__ = 'pdfcoverpage_set'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    avail = db.Column(db.Text, nullable=True, default='disable')
    """ PDF Cover Page Availability """

    header_display_type = db.Column(db.Text, nullable=True, default='string')
    """ Header Display('string' or 'image')"""

    header_output_string = db.Column(db.Text, nullable=True, default='')
    """ Header Output String"""

    header_output_image = db.Column(db.Text, nullable=True, default='')
    """ Header Output Image"""

    header_display_position = db.Column(
        db.Text, nullable=True, default='center')
    """ Header Display Position """

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    """ Created Date"""

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now)
    """ Updated Date """

    def __init__(
            self,
            avail,
            header_display_type,
            header_output_string,
            header_output_image,
            header_display_position):
        """Init."""
        self.avail = avail
        self.header_display_type = header_display_type
        self.header_output_string = header_output_string
        self.header_output_image = header_output_image
        self.header_display_position = header_display_position

    @classmethod
    def find(cls, id):
        """Find record by ID."""
        record = db.session.query(cls).filter_by(id=id).first()
        return record

    @classmethod
    def update(
            cls,
            id,
            avail,
            header_display_type,
            header_output_string,
            header_output_image,
            header_display_position):
        """Update."""
        settings = PDFCoverPageSettings(
            avail,
            header_display_type,
            header_output_string,
            header_output_image,
            header_display_position)

        """ update record by ID """
        record = db.session.query(cls).filter_by(id=id).first()

        record.avail = settings.avail
        record.header_display_type = settings.header_display_type
        record.header_output_string = settings.header_output_string
        record.header_output_image = settings.header_output_image
        record.header_display_position = settings.header_display_position

        return record


""" Record UI models """


class InstitutionName(db.Model):
    """Institution Name model."""

    id = db.Column(db.Integer, primary_key=True)
    """Identifier."""

    institution_name = db.Column(db.String(255), default='')
    """Institution name."""

    def __init__(self, name):
        """Constructor."""
        self.institution_name = name

    @classmethod
    def get_institution_name(cls):
        """Get institution name.

        Returns:
            str: institution name

        """
        institution = cls.query.first()
        if institution:
            return institution.institution_name
        return ""

    @classmethod
    def set_institution_name(cls, new_name):
        """Save institution name.

        Args:
            new_name (str): new institution name.

        """
        try:
            with db.session.begin_nested():
                cfg = cls.query.first()
                if cfg:
                    cfg.institution_name = new_name
                    db.session.merge(cfg)
                else:
                    db.session.add(cls(new_name))
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)


class FilePermission(db.Model):
    """File download permission."""

    __tablename__ = 'file_permission'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """Id."""

    user_id = db.Column(db.Integer, nullable=False)
    """User Id."""

    record_id = db.Column(db.String(255), nullable=False)
    """Record id."""

    file_name = db.Column(db.String(255), nullable=False)
    """File name."""

    usage_application_activity_id = db.Column(db.String(255), nullable=False)
    """Usage Application Activity id."""

    usage_report_activity_id = db.Column(db.String(255), nullable=True)
    """Usage Report Activity id."""

    status = db.Column(db.Integer, nullable=False)
    """Status of the permission."""
    """-1 : Initialized, 0 : Processing, 1: Approved."""

    open_date = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, user_id, record_id, file_name,
                 usage_application_activity_id,
                 usage_report_activity_id, status):
        """Init."""
        self.user_id = user_id
        self.record_id = record_id
        self.file_name = file_name
        self.usage_application_activity_id = usage_application_activity_id
        self.usage_report_activity_id = usage_report_activity_id
        self.status = status

    @classmethod
    def find(cls, user_id, record_id, file_name):
        """Find user 's permission by user_id, record_id, file_name."""
        permission = db.session.query(cls).filter_by(user_id=user_id,
                                                     record_id=record_id,
                                                     file_name=file_name)\
            .first()
        return permission

    @classmethod
    def find_list_permission_approved(cls, user_id:int, record_id:str, file_name:str):
        """Find user 's approved permission
            Args
                int:user_id
                str:record_id
                str:file_name
            Returns
                List[FilePermission]
        
        """
        list_permission:List[FilePermission] = db.session.query(cls) \
            .filter(
            cls.status == 1 # Approval
        ) \
            .filter_by(user_id=user_id,
                        record_id=record_id,
                        file_name=file_name).order_by(
            desc(cls.id)).all()
        return list_permission

    @classmethod
    def init_file_permission(cls, user_id, record_id, file_name, activity_id):
        """Init a file permission with status = Doing."""
        status_initialized = -1
        file_permission = FilePermission(user_id, record_id, file_name,
                                         activity_id, None,
                                         status_initialized
                                         )
        db.session.add(file_permission)
        return cls

    @classmethod
    def update_status(cls, permission, status):
        """Update a permission 's status."""
        permission.status = status
        db.session.merge(permission)
        return permission

    @classmethod
    def update_open_date(cls, permission, open_date):
        """Update a permission 's open date."""
        permission.open_date = open_date
        db.session.merge(permission)
        return permission

    @classmethod
    def find_by_activity(cls, activity_id):
        """Find user 's permission activity id."""
        permissions = db.session.query(cls).filter_by(
            usage_application_activity_id=activity_id).order_by(desc(cls.id)).all() 
        return permissions

    @classmethod
    def update_usage_report_activity_id(cls, permission, activity_id):
        """Update a permission 's usage report."""
        permission.usage_report_activity_id = activity_id
        db.session.merge(permission)
        return permission

    @classmethod
    def delete_object(cls, permission):
        """Delete permission object.

        @rtype: object
        """
        db.session.delete(permission)


class FileOnetimeDownload(db.Model, Timestamp):
    """A model class for the 'file_onetime_download' table.

    This class stores information about one-time URLs used for file access.

    Note:
        Despite being called 'one-time', the download limit can be set to more
        than once.

    Attributes:
        id (int): The unique identifier of the record.
        approver_id (int): The ID of the user who approved the application.
        record_id (str): The ID of the associated file record.
        file_name (str): The name of the file.
        expiration_date (datetime): The date and time when the URL expires.
        download_limit (int): The maximum number of downloads allowed.
        download_count (int): The number of times the URL has been downloaded.
        user_mail (str): The email address of the user who applied.
        is_guest (bool): Indicates whether the user is a guest.
        is_deleted (bool): Indicates whether the record is deleted.
        extra_info (dict): Additional information stored in JSON format.
            Example: {"key": "value"}.
    """
    __tablename__   = 'file_onetime_download'

    id              = db.Column(db.Integer,primary_key=True,autoincrement=True)
    approver_id     = db.Column(db.Integer, nullable=False)
    record_id       = db.Column(db.String(255), nullable=False)
    file_name       = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    download_limit  = db.Column(db.Integer, nullable=False)
    download_count  = db.Column(db.Integer, nullable=False, default=0)
    user_mail       = db.Column(db.String(255), nullable=False)
    is_guest        = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted      = db.Column(db.Boolean, nullable=False, default=False)
    extra_info      = db.Column(db.JSON()
        .with_variant(postgresql.JSONB(none_as_null=True), 'postgresql')
        .with_variant(JSONType(), 'sqlite')
        .with_variant(JSONType(), 'mysql'),
        default=lambda: dict(),
        nullable=True,
    )

    def __init__(self, approver_id, record_id, file_name, expiration_date,
                 download_limit, user_mail, is_guest, extra_info):
        """Initialize the instance.

        Args:
            approver_id (int): The ID of the user who approved the application.
            record_id (str): The ID of the file's associated record.
            file_name (str): The name of the file.
            expiration_date (datetime): The date and time when the URL expires.
            download_limit (int): The download limit of the URL.
            user_mail (str): The email address of the user who applied.
            is_guest (bool): A flag indicating whether the user is a guest.
            extra_info (dict): Additional information stored in JSON format.
        """
        self.approver_id     = approver_id
        self.record_id       = record_id
        self.file_name       = file_name
        self.expiration_date = expiration_date
        self.download_limit  = download_limit
        self.user_mail       = user_mail
        self.is_guest        = is_guest
        self.extra_info      = extra_info

    @classmethod
    def create(cls, **data):
        """Create data."""
        try:
            file_download = cls(**data)
            db.session.add(file_download)
            db.session.commit()
            return file_download
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)
            return None

    @classmethod
    def update_download(cls, **data):
        """Update download count.

        :param data:
        :return:
        """
        try:
            file_name = data.get("file_name")
            user_mail = data.get("user_mail")
            record_id = data.get("record_id")
            file_permission = cls.find(file_name=file_name, user_mail=user_mail,
                                       record_id=record_id)
            if file_permission and len(file_permission) > 0:
                for file in file_permission:
                    if data.get("download_count") is not None:
                        file.download_count = data.get("download_count")
                    if data.get("expiration_date") is not None:
                        file.expiration_date = data.get("expiration_date")
                    if data.get("extra_info"):
                        file.extra_info = data.get("extra_info")
                    db.session.merge(file)
                db.session.commit()
                return file_permission
            return None
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)
            return None

    @classmethod
    def find(cls, **obj) -> list:
        """Find file onetime download.

        :param obj:
        :return:
        """
        query = db.session.query(cls).filter(
            cls.file_name == obj.get("file_name"),
            cls.record_id == obj.get("record_id"),
            cls.user_mail == obj.get("user_mail"),
        )
        return query.order_by(desc(cls.id)).all()

    @classmethod
    def find_downloadable_only(cls, **obj) -> list:
        """If the user can download ,find file onetime download.

        :param obj:
        :return:
        """
        query = db.session.query(cls).filter(
            cls.file_name == obj.get("file_name"),
            cls.record_id == obj.get("record_id"),
            cls.user_mail == obj.get("user_mail"),
            cls.download_count > 0 ,
            now() < cls.created  + func.cast( concat( cls.expiration_date , ' days' ) , INTERVAL)
        )
        return query.order_by(desc(cls.id)).all()


class FileSecretDownload(db.Model, Timestamp):
    """A model class for file secret download.

    This class stores information about secret URLs used for file access.

    Attributes:
        id (int): The identifier of the record.
        creator_id (int): The ID of the user who issued the secret URL.
        record_id (str): The ID of the record that has the file.
        file_name (str): The name of the file.
        label_name (str): The label of the secret URL.
        expiration_date (datetime): The date and time when the URL expires.
        download_limit (int): The download limit of the URL.
        download_count (int): The number of times the URL has been downloaded.
        is_deleted (bool): A flag indicating whether the record is deleted.
    """
    __tablename__ = 'file_secret_download'

    id              = db.Column(db.Integer,primary_key=True,autoincrement=True)
    creator_id      = db.Column(db.Integer,
                                db.ForeignKey(
                                    'accounts_user.id',
                                    name='fk_file_secret_download_creator_id'),
                                nullable=False)
    record_id       = db.Column(db.String(255), nullable=False)
    file_name       = db.Column(db.String(255), nullable=False)
    label_name      = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    download_limit  = db.Column(db.Integer, nullable=False)
    download_count  = db.Column(db.Integer, nullable=False, default=0)
    is_deleted      = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, creator_id, record_id, file_name, label_name,
                 expiration_date, download_limit):
        """Initialize the instance.

        Args:
            creator_id (int): The ID of the user who issued the secret URL.
            record_id (str): The ID of the record that has the file.
            file_name (str): The name of the file.
            label_name (str): The label of the secret URL.
            expiration_date (datetime): The date and time when the URL expires.
            download_limit (int): The download limit of the URL.
        """
        self.creator_id = creator_id
        self.record_id = record_id
        self.file_name = file_name
        self.label_name = label_name
        self.expiration_date = expiration_date
        self.download_limit = download_limit

    @classmethod
    def create(cls, **data):
        """Create data."""
        try:
            file_download = cls(**data)
            db.session.add(file_download)
            db.session.commit()
            db.session.flush()
            return file_download
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)
            raise ex

    def update(self, **data):
        """Update FileSecretDownload object.

        Args:
            data (dict): The data to update.

        Returns:
            FileSecretDownload: The updated object.
        """
        try:
            for key, value in data.items():
                setattr(self, key, value)
            db.session.commit()
            return self
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)
            raise ex

    @classmethod
    def update_download(cls, **data):
        """Update download count.

        :param data:
        :return:
        """
        try:
            file_name = data.get("file_name")
            id = data.get("id")
            record_id = data.get("record_id")
            created = data.get("created")
            file_permission = cls.find(file_name=file_name, id=id,
                                        record_id=record_id, created=created)
            if len(file_permission) == 1:
                file = file_permission[0]
                if data.get("download_count") is not None:
                    file.download_count = data.get("download_count")
                db.session.merge(file)
                db.session.commit()
                return file_permission
            else:
                return None
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(traceback.format_exc())
            raise ex

    @classmethod
    def find(cls, **obj) -> list:
        """Find file onetime download.

        :param obj:
        :return:
        """
        query = db.session.query(cls).filter(
            cls.id == obj.get("id"),
            cls.file_name == obj.get("file_name"),
            cls.record_id == obj.get("record_id"),
            cls.created == obj.get("created")
        )
        return query.order_by(desc(cls.id)).all()

    @classmethod
    def get_by_id(cls, obj_id):
        """Retrieve an object by its ID.

        Args:
            obj_id (int): The ID of the object to retrieve.

        Returns:
            cls: The object with the specified ID, or None if not found.
        """
        obj = cls.query.filter_by(id=obj_id).first()
        return obj


class UrlType(enum.Enum):
    """An ENUM data type for the used URL type."""
    SECRET = 'SECRET'
    ONETIME = 'ONETIME'


class AccessStatus(enum.Enum):
    """An ENUM data type for the access status of the downloaded file."""
    OPEN_NO = 'OPEN_NO'
    OPEN_DATE = 'OPEN_DATE'
    OPEN_RESTRICTED = 'OPEN_RESTRICTED'


class FileUrlDownloadLog(db.Model, Timestamp):
    """A model class for the table 'file_url_download_log.'

    This class is used to store the information of the executed download of the
    file using either secret URL or onetime URL.

    Attributes:
        id (int): The identifier of the record.
        url_type (UrlType): The used URL type.
        secret_url_id (int): The secret URL record ID.
        onetime_url_id (int): The onetime URL record ID.
        ip_address (str): The IP address of the downloader.
        access_status (AccessStatus): The access status of the downloaded file.
        used_token (str): The URL token used to access the file.
    """

    __tablename__ = 'file_url_download_log'
    __table_args__ = (
        CheckConstraint(
            "("
            "(url_type = 'SECRET' AND secret_url_id IS NOT NULL AND "
            "onetime_url_id IS NULL) OR "
            "(url_type = 'ONETIME' AND onetime_url_id IS NOT NULL AND "
            "secret_url_id IS NULL)"
            ")",
            name="chk_url_type",
        ),
    )

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    url_type = db.Column(db.Enum(UrlType), nullable=False)
    secret_url_id = db.Column(
        db.Integer(), db.ForeignKey(FileSecretDownload.id))
    onetime_url_id = db.Column(
        db.Integer(), db.ForeignKey(FileOnetimeDownload.id))
    ip_address = db.Column(INET()
        .with_variant(db.String(255), 'sqlite')
        .with_variant(db.String(255), 'mysql'))
    access_status = db.Column(db.Enum(AccessStatus), nullable=False)
    used_token = db.Column(db.String(255), nullable=False)

    def __init__(self, url_type, secret_url_id, onetime_url_id, ip_address,
                 access_status, used_token):
        """Initializes the instance.
        
        Args:
            url_type (UrlType): The used URL type.
            secret_url_id (int): The secret URL record ID.
            onetime_url_id (int): The onetime URL record ID.
            ip_address (str): The IP address of the downloader.
            access_status (AccessStatus): The status of the downloaded file.
            used_token (str): The URL token used to access the file.
        """
        self.url_type = url_type
        self.secret_url_id = secret_url_id
        self.onetime_url_id = onetime_url_id
        self.ip_address = ip_address
        self.access_status = access_status
        self.used_token = used_token

    @classmethod
    def create(cls, **data):
        """Create a new record.
        
        Args:
            data (dict): The data to create the record.
        
        Returns:
            FileUrlDownloadLog: The created record.
        """
        try:
            dl_log = cls(**data)
            db.session.add(dl_log)
            db.session.commit()
            return dl_log
        except Exception as ex:
            db.session.rollback()
            current_app.logger.error(ex)
            return None

class RocrateMapping(db.Model, Timestamp):
    """Represent a mapping from metadata to ro-crate.
    The RocrateMapping object contains a ``created`` and  a ``updated`` properties that are automatically updated.
    """

    __tablename__ = 'rocrate_mapping'

    id = db.Column(
        db.Integer(),
        primary_key=True,
        autoincrement=True
    )
    """Record identifier."""

    item_type_id = db.Column(
        db.Integer,
        db.ForeignKey(ItemType.id),
        unique=True,
        nullable=False,
    )
    """ID of item type."""

    mapping = db.Column(
        db.JSON().with_variant(
            postgresql.JSONB(none_as_null=True),
            'postgresql',
        ).with_variant(
            JSONType(),
            'sqlite',
        ).with_variant(
            JSONType(),
            'mysql',
        ),
        default=lambda: dict(),
        nullable=True
    )
    """Store mapping in JSON format."""

    def __init__(self, item_type_id, mapping):
        """Init.

        :param item_type_id: item type id
        :param mapping: mapping from metadata to RO-Crate
        """
        self.item_type_id = item_type_id
        self.mapping = mapping


__all__ = (
    'PDFCoverPageSettings',
    'FilePermission',
    'FileOnetimeDownload',
    'FileSecretDownload',
    'FileUrlDownloadLog'
    'RocrateMapping'
)
