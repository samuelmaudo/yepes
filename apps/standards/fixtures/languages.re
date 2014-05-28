
^([0-9]+);([a-z]+);([a-z]{2,3});([a-z]{,2});([a-z]{,3});([a-z]{,3});([^;]+);
  {\n    "model": "standards.Language",\n    "pk": \1,\n    "fields": {\n      "is_enabled": \2,\n      "tag": "\3",\n      "iso_639_1": "\4",\n      "iso_639_2": "\5",\n      "iso_639_3": "\6",\n      "name": "\7",

,([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)$
,\n      "name_de": "\1",\n      "name_en": "\2",\n      "name_es": "\3",\n      "name_fr": "\4",\n      "name_pt": "\5",\n      "name_ru": "\6",\n      "name_zh": "\7"\n    }\n  },
