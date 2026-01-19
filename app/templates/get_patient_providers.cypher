MATCH path = (p:Patient)-[r1]-(provider:Practitioner|Organization)
WHERE p.id = "{{ patient_id }}"
AND provider.name is not NULL
WITH provider, apoc.convert.fromJsonMap(provider.telecom) as telecom, apoc.convert.fromJsonMap(provider.contact) as contact
RETURN DISTINCT
    LABELS(provider)[0] as providerType,
    CASE WHEN LABELS(provider)[0] = "Practitioner" THEN apoc.convert.fromJsonMap(provider.name).text ELSE provider.name END AS name,
    telecom,
    contact.address.line[0] as address,
    contact.address.city as city,
    contact.address.state as state,
    contact.address.postalCode as postalCode
        