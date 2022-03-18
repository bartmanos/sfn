# Generated by Django 4.0.3 on 2022-03-17 20:19

from django.db import migrations


def apply_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Poi = apps.get_model("core", "Poi")

    group = Group.objects.get(name='POI admin')
    content_type = ContentType.objects.get_for_model(Poi)
    perms = ['add_goods', 'change_goods', 'add_needs', 'change_needs', 'delete_needs', 'change_poi']
    for perm in perms:
        permission = Permission.objects.get(codename=perm)
        group.permissions.add(permission)

    group = Group.objects.get(name='POI user')
    content_type = ContentType.objects.get_for_model(Poi)
    perms = ['add_needs']
    for perm in perms:
        permission = Permission.objects.get(codename=perm)
        group.permissions.add(permission)


def revert_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_goods_poi'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration)
    ]