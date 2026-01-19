# Generated manually for provider profile enhancements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0005_quoterequest_is_emergency_and_more'),
    ]

    operations = [
        # Add new fields to ServiceProvider
        migrations.AddField(
            model_name='serviceprovider',
            name='is_draft',
            field=models.BooleanField(default=True, help_text='Profile is in draft mode and not visible to public'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='approval_status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('pending_review', 'Pending Review'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('suspended', 'Suspended'),
                ],
                default='draft',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='email_verification_token',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='submitted_for_review_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='Reason for rejection if applicable'),
        ),
        
        # Create BusinessHours model
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monday_open', models.TimeField(blank=True, null=True)),
                ('monday_close', models.TimeField(blank=True, null=True)),
                ('monday_closed', models.BooleanField(default=False)),
                ('tuesday_open', models.TimeField(blank=True, null=True)),
                ('tuesday_close', models.TimeField(blank=True, null=True)),
                ('tuesday_closed', models.BooleanField(default=False)),
                ('wednesday_open', models.TimeField(blank=True, null=True)),
                ('wednesday_close', models.TimeField(blank=True, null=True)),
                ('wednesday_closed', models.BooleanField(default=False)),
                ('thursday_open', models.TimeField(blank=True, null=True)),
                ('thursday_close', models.TimeField(blank=True, null=True)),
                ('thursday_closed', models.BooleanField(default=False)),
                ('friday_open', models.TimeField(blank=True, null=True)),
                ('friday_close', models.TimeField(blank=True, null=True)),
                ('friday_closed', models.BooleanField(default=False)),
                ('saturday_open', models.TimeField(blank=True, null=True)),
                ('saturday_close', models.TimeField(blank=True, null=True)),
                ('saturday_closed', models.BooleanField(default=False)),
                ('sunday_open', models.TimeField(blank=True, null=True)),
                ('sunday_close', models.TimeField(blank=True, null=True)),
                ('sunday_closed', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about availability')),
                ('provider', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_hours', to='providers.serviceprovider')),
            ],
            options={
                'verbose_name': 'Business Hours',
                'verbose_name_plural': 'Business Hours',
            },
        ),
        
        # Create ServiceArea model
        migrations.CreateModel(
            name='ServiceArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('radius_miles', models.PositiveIntegerField(default=25, help_text='Service radius in miles from this location')),
                ('is_primary', models.BooleanField(default=False, help_text='Primary service location')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_areas', to='providers.serviceprovider')),
            ],
            options={
                'verbose_name': 'Service Area',
                'verbose_name_plural': 'Service Areas',
                'ordering': ['-is_primary', 'city', 'state'],
            },
        ),
        
        # Create ProviderCertification model
        migrations.CreateModel(
            name='ProviderCertification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., "Licensed Electrician"', max_length=200)),
                ('issuing_organization', models.CharField(blank=True, max_length=200)),
                ('license_number', models.CharField(blank=True, max_length=100)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('verification_document', models.FileField(blank=True, help_text='Upload verification document', null=True, upload_to='certifications/')),
                ('is_verified', models.BooleanField(default=False, help_text='Admin verified certification')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to='providers.serviceprovider')),
            ],
            options={
                'verbose_name': 'Provider Certification',
                'verbose_name_plural': 'Provider Certifications',
                'ordering': ['-is_verified', '-issue_date'],
            },
        ),
    ]
