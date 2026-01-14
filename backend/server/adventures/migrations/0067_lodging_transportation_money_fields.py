from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("adventures", "0066_collection_primary_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="lodging",
            name="price_currency",
            field=djmoney.models.fields.CurrencyField(
                default="USD", editable=False, max_length=3
            ),
        ),
        migrations.AddField(
            model_name="transportation",
            name="price_currency",
            field=djmoney.models.fields.CurrencyField(
                default="USD", editable=False, max_length=3
            ),
        ),
        migrations.AlterField(
            model_name="lodging",
            name="price",
            field=djmoney.models.fields.MoneyField(
                blank=True,
                decimal_places=2,
                default_currency="USD",
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="transportation",
            name="price",
            field=djmoney.models.fields.MoneyField(
                blank=True,
                decimal_places=2,
                default_currency="USD",
                max_digits=12,
                null=True,
            ),
        ),
    ]
