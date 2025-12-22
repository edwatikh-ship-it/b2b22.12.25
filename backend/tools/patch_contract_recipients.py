import yaml

p = r"D:\b2bplatform\api-contracts.yaml"
with open(p, encoding="utf-8") as f:
    spec = yaml.safe_load(f)

schemas = spec.setdefault("components", {}).setdefault("schemas", {})

schemas["UpdateRecipientsRequest"] = {
    "type": "object",
    "properties": {
        "recipients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "supplierid": {"type": "integer"},
                    "selected": {"type": "boolean"},
                },
                "required": ["supplierid", "selected"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["recipients"],
    "additionalProperties": False,
}

schemas["RecipientsResponse"] = {
    "type": "object",
    "properties": {
        "recipients": {
            "$ref": "#/components/schemas/UpdateRecipientsRequest/properties/recipients"
        },
    },
    "required": ["recipients"],
    "additionalProperties": False,
}

put_op = spec["paths"]["/user/requests/{requestId}/recipients"]["put"]
put_op["requestBody"]["content"]["application/json"]["schema"] = {
    "$ref": "#/components/schemas/UpdateRecipientsRequest"
}

put_op["responses"] = {
    "200": {
        "description": "Successful Response",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/RecipientsResponse"}}
        },
    }
}

with open(p, "w", encoding="utf-8") as f:
    f.write(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True))

print("patched ok")
