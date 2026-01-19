MATCH (p:Patient)-[r1:HAS_ENCOUNTER]-(e:Encounter)
WHERE p.id = "{{ patient_id }}"
WITH e, apoc.convert.fromJsonMap(e.type) as encounterType, apoc.convert.fromJsonMap(e.class) as classification
RETURN DISTINCT
    e.actualPeriodStartDate as startDate,
    e.actualPeriodEndDate as endDate,
    COALESCE(classification.text, classification.coding[0].display) as encounterClassification,
    COALESCE(encounterType.text, encounterType.coding[0].display) as encounterType
    