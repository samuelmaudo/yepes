# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.datamigrations.importation_plans import ModelImportationPlan
from yepes.loading import LazyModel
from yepes.utils.emails import normalize_email, validate_email

Domain = LazyModel('newsletters', 'Domain')
Newsletter = LazyModel('newsletters', 'Newsletter')
SubscriberTag = LazyModel('newsletters', 'SubscriberTag')


class SubscriberPlan(ModelImportationPlan):

    updates_data = False

    def import_batch(self, batch):
        model = self.migration.model
        key = self.migration.primary_key.attname
        existing_keys = self.get_existing_keys(batch)
        for row in batch:
            if row[key] in existing_keys:
                continue

            address = normalize_email(row['email_address'])
            if not validate_email(address):
                msg = "'{0}' is not a valid email address."
                raise ValueError(msg.format(address))

            _, domain_name = address.rsplit('@', 1)
            domain, _ = Domain.cache.get_or_create(name=domain_name)

            row['email_address'] = address
            row['email_domain'] = domain

            newsletter_names = row.pop('newsletters', False)
            tag_names = row.pop('tags', False)

            obj = model(**row)
            obj.save(force_insert=True)

            if newsletter_names:
                if ',' in newsletter_names:
                    newsletter_names = newsletter_names.split(',')
                elif '|' in newsletter_names:
                    newsletter_names = newsletter_names.split('|')
                else:
                    newsletter_names = [newsletter_names]

                for name in newsletter_names:
                    newsletter = Newsletter.cache.get(name=name)
                    if newsletter is not None:
                        obj.subscriptions.create(newsletter=newsletter)

            if tag_names:
                if ',' in tag_names:
                    tag_names = tag_names.split(',')
                elif '|' in tag_names:
                    tag_names = tag_names.split('|')
                else:
                    tag_names = [tag_names]

                for name in tag_names:
                    tag, _ = SubscriberTag.cache.get_or_create(name=name)
                    obj.tags.add(tag)

