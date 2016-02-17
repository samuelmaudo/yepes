
^([0-9]+);([a-z]+);([0-9]+);([A-Z]{2});([A-Z]{3});([0-9]{3});([^;]+);
  {\n    "model": "standards.Country",\n    "pk": \1,\n    "fields": {\n      "is_enabled": \2,\n      "region": \3,\n      "code": "\4",\n      "long_code": "\5",\n      "number": "\6",\n      "name": "\7",

,([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)$
,\n      "name_de": "\1",\n      "name_en": "\2",\n      "name_es": "\3",\n      "name_fr": "\4",\n      "name_pt": "\5",\n      "name_ru": "\6",\n      "name_zh": "\7"\n    }\n  },
