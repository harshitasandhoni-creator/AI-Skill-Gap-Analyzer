-- SQLite

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
