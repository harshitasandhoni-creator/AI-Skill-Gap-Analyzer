SELECT COUNT(*) AS total_roles
FROM roles;
SELECT
    skill_name,
    platform,
    resource_title,
    resource_url,
    resource_type
FROM learning_resources;

SELECT
    skill_name,
    platform,
    resource_title,
    resource_url,
    COUNT(*) AS total_entries
FROM learning_resources
GROUP BY
    skill_name,
    platform,
    resource_title,
    resource_url
HAVING COUNT(*) > 1;

