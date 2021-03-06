# Generated by Django 2.2.3 on 2019-07-11 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20190710_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='released',
            field=models.DateField(default='1990-10-11'),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(help_text='17 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>', max_length=17, verbose_name='ISBN'),
        ),
    ]
