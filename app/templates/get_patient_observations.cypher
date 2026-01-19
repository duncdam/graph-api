MATCH (p:Patient)-[r1:HAS_OBSERVATION]-(o:Observation)
WHERE p.id = "{{ patient_id }}"
OPTIONAL MATCH (o)-[r2:ENCODED_AS]-(q:Code)
OPTIONAL MATCH (dr:DiagnosticReport)-[r3:HAS_PART]->(o)
WITH p,o,q, dr, apoc.convert.fromJsonMap(o.category) as cat, apoc.convert.fromJsonMap(o.valueCodeableConcept) as valueCodeableConcept
RETURN 
    o.effectivePeriodStartDate as startDate,
    COALESCE (o.effectivePeriodEndDate,o.effectiveDosePeriodEndDate) as endDate,
    apoc.coll.toSet(
        [text in COALESCE(dr.displayText, []) WHERE text IS NOT NULL | toLower(text)]
    ) as diagnosticReport,
    o.observationType as observationType,
    apoc.coll.toSet(
        [text in COALESCE(o.displayText, []) WHERE text IS NOT NULL | toLower(text)] + 
        [text in COALESCE([q.name], []) WHERE text IS NOT NULL | toLower(text)]
    ) as observation,
    q.code as observationCode,
    q.system as codeSystem,
    COALESCE (o.valueText, o.valueString) as valueText,
    {% raw %}
    COALESCE (
        apoc.convert.fromJsonMap(o.valueQuantity),
        {
            name:valueCodeableConcept["coding"][0]["display"],
            code:valueCodeableConcept["coding"][0]["code"],
            system:valueCodeableConcept["coding"][0]["codeSystemName"]
        }
    ) as valueQuantity,
    {% endraw %}
    cat["coding"][0]["code"] as category