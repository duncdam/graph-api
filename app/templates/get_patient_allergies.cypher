MATCH path = (p:Patient)-[r1:HAS_ALLERGY]-(a:Allergy)
WHERE p.id = "{{ patient_id }}"
OPTIONAL MATCH (a)-[r2:ENCODED_AS]-(ac:Code)
OPTIONAL MATCH (a)-[:CAUSED]->(r:Reaction)
OPTIONAL MATCH (r)-[:ENCODED_AS]->(rc:Code)
WITH p, a, r, ac, rc, apoc.convert.fromJsonMap(a.type) as allergyType, apoc.convert.fromJsonMap(r.severity) as reactionSeverity
RETURN DISTINCT
    COALESCE(a.recordedDate, a.onsetPeriodStartDate) as allergyRecordedDate,
    apoc.coll.toSet(
        [text in COALESCE(a.displayText, []) WHERE text IS NOT NULL | toLower(text)] + 
        [text in COALESCE([ac.name], []) WHERE text IS NOT NULL | toLower(text)]
    ) as allergy,
    ac.code as allergyCode, 
    ac.system as codeSystem,
    allergyType.coding[0].display as allergyType, 
    r.onset as reactionRecordedDate, 
    reactionSeverity.coding[0].display as reactionSeverity