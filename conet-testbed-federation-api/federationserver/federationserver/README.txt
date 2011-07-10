INTRODUCTION

how to dump the database to a JSON file

python manage.py dumpdata api auth > initial_data.json

GUIDELINES FOR USING THE API

PROJECT

for POST and PUT this should be the request body
all fields are mandatory (and updated)

example:

POST /projects/

{
    description: "baubau"
    name: "ciao"
}


EXPERIMENT

for POST and PUT this should be the request body
all fields are mandatory (and updated)

example:

POST /experiments/

{
    description: "baubau"
    project: "3678813f"
    name: "ciao"
}