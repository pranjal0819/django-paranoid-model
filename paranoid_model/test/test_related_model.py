from django.test import TestCase
from paranoid_model.test.models import Person, Phone
from faker import Faker
from paranoid_model.test.utils import (
    any_list, all_list, get_person_instance, create_list_of_person,
    get_phone_instace
)
from paranoid_model.paranoid_model import SoftDeleted


fake = Faker('en_US')


class RelatedModelTest(TestCase):
    """Test model with relatioships ManyToMany, ForeignKey, OneToOne"""
    
    def setUp(self):
        pass

    def assertNotRaises(self, function):
        """
        Method to check if a function does not raises an exception
        Args:
            function: callback function name
        """
        try:
            function()
        except Exception as exc:
            self.fail('Raised in a query that was not suposed to! Message: {}'.format(exc))

    def test_create(self):
        """Test creation of a related model"""
        person = get_person_instance()
        person.save()
        get_phone_instace(person).save()

        all_phones = person.phones.all()
        self.assertEquals(all_phones.count(), 1)
    
    def test_related_name_queries_all(self):
        """Test related name query .all()"""
        person = get_person_instance()
        person.save()
        
        phone1 = get_phone_instace(person)
        phone1.save()
        phone2 = get_phone_instace(person)
        phone2.save()

        self.assertEquals(person.phones.all().count(), 2)

        phone1.delete()
        self.assertEquals(person.phones.all().count(), 1)
        self.assertEquals(person.phones.all(with_deleted=True).count(), 2)
        
        phone1.restore()
        person.delete()
        self.assertEquals(person.phones.all().count(), 2)
        self.assertEquals(person.phones.all(with_deleted=True).count(), 2)
        self.assertEquals(person.phones.all(with_deleted=False).count(), 0)
    
    def test_related_name_queries_filter(self):
        """Test related name query .filter()"""
        person = get_person_instance()
        person.save()
        
        phone1 = get_phone_instace(person)
        phone1.save()
        phone2 = get_phone_instace(person)
        phone2.save()
        
        phone1.delete()
        self.assertEquals(person.phones.filter(owner=person).count(), 1)
        self.assertEquals(person.phones.filter(owner=person, with_deleted=True).count(), 2)
        self.assertEquals(person.phones.filter(owner=person, with_deleted=False).count(), 1)
    
    def test_get_on_related(self):
        """Test .get() wiht related_name query"""

        person = get_person_instance()
        person.save()

        phone1 = get_phone_instace(person)
        phone1.save()

        self.assertNotRaises(lambda: person.phones.get(phone=phone1.phone))
        self.assertRaises(Phone.DoesNotExist, lambda: person.phones.get(phone=phone1.phone+'0'))
        phone1.delete()

        self.assertRaises(Phone.SoftDeleted, lambda: person.phones.get(phone=phone1.phone))
        self.assertRaises(Phone.DoesNotExist, lambda: person.phones.get(phone=phone1.phone+'0'))

    def test_get_deleted(self):
        """Test .get_deleted() wiht related_name query"""

        person = get_person_instance()
        person.save()

        phone1 = get_phone_instace(person)
        phone1.save()
        phone2 = get_phone_instace(person)
        phone2.save()
        phone2.delete()

        self.assertRaises(
            Phone.IsNotSoftDeleted,
            lambda: person.phones.get_deleted(phone=phone1.phone))

        self.assertNotRaises(
            lambda: person.phones.get_deleted(phone=phone2.phone))
        
        self.assertRaises(
            Phone.MultipleObjectsReturned,
            lambda: person.phones.get(owner=person))