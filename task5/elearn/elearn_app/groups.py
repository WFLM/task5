from django.contrib.auth.models import Group, Permission

# data migration -> to migrations

teachers, created = Group.objects.get_or_create(name="Teachers")
if created:
    teachers.permissions.add(
        Permission.objects.get(name="Can add course"),
        Permission.objects.get(name="Can view course"),
        Permission.objects.get(name="Can change course"),
        Permission.objects.get(name="Can delete course"),

        Permission.objects.get(name="Can add lecture"),
        Permission.objects.get(name="Can view lecture"),
        Permission.objects.get(name="Can change lecture"),
        Permission.objects.get(name="Can delete lecture"),

        Permission.objects.get(name="Can add homework"),
        Permission.objects.get(name="Can view homework"),
        Permission.objects.get(name="Can change homework"),
        Permission.objects.get(name="Can delete homework"),

        Permission.objects.get(name="Can add homework instance"),
        Permission.objects.get(name="Can view homework instance"),
        Permission.objects.get(name="Can change homework instance"),
        # Permission.objects.get(name="Can delete homework instance"),

        Permission.objects.get(name="Can add homework instance mark"),
        Permission.objects.get(name="Can view homework instance mark"),
        Permission.objects.get(name="Can change homework instance mark"),
        # Permission.objects.get(name="Can delete homework instance mark"),


        Permission.objects.get(name="Can add homework instance comment"),
        Permission.objects.get(name="Can view homework instance comment"),
        # Permission.objects.get(name="Can change homework instance comment"),
        # Permission.objects.get(name="Can delete homework instance comment"),
    )


students, created = Group.objects.get_or_create(name="Students")
if created:
    students.permissions.add(
        # Permission.objects.get(name="Can add course"),
        Permission.objects.get(name="Can view course"),
        # Permission.objects.get(name="Can change course"),
        # Permission.objects.get(name="Can delete course"),

        # Permission.objects.get(name="Can add lecture"),
        Permission.objects.get(name="Can view lecture"),
        # Permission.objects.get(name="Can change lecture"),
        # Permission.objects.get(name="Can delete lecture"),

        # Permission.objects.get(name="Can add homework"),
        Permission.objects.get(name="Can view homework"),
        # Permission.objects.get(name="Can change homework"),
        # Permission.objects.get(name="Can delete homework"),

        Permission.objects.get(name="Can add homework instance"),
        Permission.objects.get(name="Can view homework instance"),
        Permission.objects.get(name="Can change homework instance"),
        # Permission.objects.get(name="Can delete homework instance"),

        # Permission.objects.get(name="Can add homework instance mark"),
        Permission.objects.get(name="Can view homework instance mark"),
        # Permission.objects.get(name="Can change homework instance mark"),
        # Permission.objects.get(name="Can delete homework instance mark"),

        Permission.objects.get(name="Can add homework instance comment"),
        Permission.objects.get(name="Can view homework instance comment"),
        # Permission.objects.get(name="Can change homework instance comment"),
        # Permission.objects.get(name="Can delete homework instance comment"),
    )
