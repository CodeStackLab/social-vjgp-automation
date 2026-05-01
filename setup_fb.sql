USE mixpost;
INSERT INTO mixpost_services (name, configuration, active) 
VALUES ("facebook", "{\"client_id\":\"1901738023959051\",\"client_secret\":\"916d8723044900700580a7fcbede5d0a\"}", 1) 
ON DUPLICATE KEY UPDATE configuration = VALUES(configuration), active = 1;
