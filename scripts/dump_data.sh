#!/bin/sh

python3 ../manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e sessions -e admin \
django_celery_beat.crontabschedule \
django_celery_beat.periodictasks \
django_celery_beat.periodictask \
django_celery_results.taskresult \
subscription.subscription \
authentication.user \
authentication.role \
property.propertyupcomingactivity \
property.property \
property.propertylatefeepolicy \
property.propertyattachment \
property.propertyleasetemplateattachment \
property.propertyleaserenewalattachment \
property.propertyphoto \
property.propertyowner \
property.rentableitem \
property.unittype \
property.unittypephoto \
property.unit \
property.unitupcomingactivity \
property.unitphoto \
lease.leasetemplate \
lease.rentalapplicationtemplate \
lease.secondarytenant \
lease.rentalapplicationemergencycontact \
lease.rentalapplicationresidentialhistory \
lease.rentalapplicationfinancialinformation \
lease.rentalapplicationadditionalincome \
lease.rentalapplicationdependent \
lease.rentalapplicationpets \
lease.rentalapplicationattachment \
lease.applicant \
lease.rentalapplication \
lease.lease \
people.tenant \
people.tenantupcomingactivity \
people.tenantattachment \
people.vendortype \
people.vendor \
people.vendoraddress \
people.vendorattachment \
people.ownerupcomingactivity \
people.owner \
maintenance.servicerequest \
maintenance.workorder \
maintenance.inspection \
maintenance.area \
maintenance.areaitem \
maintenance.project \
maintenance.projectexpense \
maintenance.labor \
maintenance.purchaseorder \
maintenance.inventory \
maintenance.purchaseorderitem \
maintenance.fixedasset \
communication.contact \
communication.note \
communication.noteattachment \
communication.emailsignature \
communication.emailtemplate \
communication.email \
communication.emailattachment \
communication.announcement \
communication.announcementattachment \
system_preferences.propertytype \
system_preferences.inventoryitemtype \
system_preferences.tag \
system_preferences.label \
system_preferences.inventorylocation \
system_preferences.managementfee \
system_preferences.businessinformation \
system_preferences.contactcategory \
accounting.chargeattachment \
accounting.charge \
accounting.invoice \
-o ../fixtures/dev-environment-and-tests.json
