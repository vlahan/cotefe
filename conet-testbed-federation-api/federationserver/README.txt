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