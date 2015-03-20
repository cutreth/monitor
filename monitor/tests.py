from django.test import TestCase

from monitor.views import intFromPost, floatFromPost, stringFromPost, allDataBlank, allDataPositive
from django.http import HttpRequest, QueryDict

def buildValidRequestObject():
    request = HttpRequest()
    request.POST = QueryDict('float=2.56&int=6&string=dog')
    return request

def buildInvalidRequestObject_1():
    request = HttpRequest()
    request.POST = QueryDict('float=cat6&int=-6.4&string=(*)')
    return request

def buildInvalidRequestObject_2():
    request = HttpRequest()
    request.POST = QueryDict('float=-7.56&int=mouse&string=75F')
    return request

def buildZeroRequestObject():
    request = HttpRequest()
    request.POST = QueryDict('float=0&int=0&string=0')
    return request
    
def buildBlankRequestObject():
    request = HttpRequest()
    request.POST = QueryDict('')
    return request

class ApiTestCases(TestCase):
    
    def test_intFromPost_1(self):
        request = buildValidRequestObject()
        value = intFromPost(request,'int')
        self.assertEqual(type(value),type(int(1)))
        
    def test_intFromPost_2(self):
        request = buildInvalidRequestObject_1()
        value = intFromPost(request,'int')
        self.assertEqual(type(value),type(int(1)))
    
    def test_intFromPost_3(self):
        request = buildInvalidRequestObject_2()
        value = intFromPost(request,'int')
        self.assertEqual(type(value),type(int(1)))
        
    def test_intFromPost_4(self):
        request = buildZeroRequestObject()
        value = intFromPost(request,'int')
        self.assertEqual(value,0)
        
    def test_intFromPost_5(self):
        request = buildBlankRequestObject()
        value = intFromPost(request,'int')
        self.assertEqual(value,0)
        
    def test_floatFromPost_1(self):
        request = buildValidRequestObject()
        value = floatFromPost(request,'float')
        self.assertEqual(type(value),type(float(1)))
        
    def test_floatFromPost_2(self):
        request = buildInvalidRequestObject_1()
        value = floatFromPost(request,'float')
        self.assertEqual(type(value),type(float(1)))
    
    def test_floatFromPost_3(self):
        request = buildInvalidRequestObject_2()
        value = floatFromPost(request,'float')
        self.assertEqual(type(value),type(float(1)))
        
    def test_floatFromPost_4(self):
        request = buildZeroRequestObject()
        value = floatFromPost(request,'float')
        self.assertEqual(value,0)            
        
    def test_floatFromPost_5(self):
        request = buildBlankRequestObject()
        value = floatFromPost(request,'float')
        self.assertEqual(value,0)      
        
    def test_stringFromPost_1(self):
        request = buildValidRequestObject()
        value = stringFromPost(request,'string')
        self.assertEqual(type(value),type(str(1)))
        
    def test_stringFromPost_2(self):
        request = buildInvalidRequestObject_1()
        value = stringFromPost(request,'string')
        self.assertEqual(type(value),type(str(1)))
    
    def test_stringFromPost_3(self):
        request = buildInvalidRequestObject_2()
        value = stringFromPost(request,'string')
        self.assertEqual(type(value),type(str(1)))
        
    def test_stringFromPost_4(self):
        request = buildZeroRequestObject()
        value = stringFromPost(request,'string')
        self.assertEqual(value,str(''))
        
    def test_stringFromPost_5(self):
        request = buildBlankRequestObject()
        value = stringFromPost(request,'string')
        self.assertEqual(value,str(''))    
        
    def test_allDataBlank_1(self):
        sensor_data = [float(0), float(0), float(0)]
        result = allDataBlank(sensor_data)
        self.assertEqual(result, True)
        
    def test_allDataBlank_2(self):
        sensor_data = [float(1), float(0), float(0)]
        result = allDataBlank(sensor_data)
        self.assertEqual(result, False)
        
    def test_allDataBlank_3(self):
        sensor_data = [float(1), float(1), float(1)]
        result = allDataBlank(sensor_data)
        self.assertEqual(result, False)
        
    def test_allDataBlank_4(self):
        sensor_data = [float(-1), float(0), float(1)]
        result = allDataBlank(sensor_data)
        self.assertEqual(result, False)
        
    def test_allDataBlank_5(self):
        sensor_data = [float(-1), float(0), float(0)]
        result = allDataBlank(sensor_data)
        self.assertEqual(result, True)
        
    def test_allDataPositive_1(self):
        sensor_data = [float(0), float(0), float(0)]
        result = allDataPositive(sensor_data)
        self.assertEqual(result, True)
        
    def test_allDataPositive_2(self):
        sensor_data = [float(1), float(0), float(0)]
        result = allDataPositive(sensor_data)
        self.assertEqual(result, True)

    def test_allDataPositive_3(self):
        sensor_data = [float(-1), float(1), float(1)]
        result = allDataPositive(sensor_data)
        self.assertEqual(result, False)

    def test_allDataPositive_4(self):
        sensor_data = [float(-1), float(-1), float(-1)]
        result = allDataPositive(sensor_data)
        self.assertEqual(result, False)

    def test_allDataPositive_5(self):
        sensor_data = [float(1), float(1), float(1)]
        result = allDataPositive(sensor_data)
        self.assertEqual(result, True)