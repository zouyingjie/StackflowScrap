# -*- coding: utf-8 -*-
class ManyRequestException(Exception):

    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        print(self.desc)