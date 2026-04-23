db = db.getSiblingDB('blog_db');

db.createCollection("posts", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["titre", "auteur", "vues"],
         properties: {
            titre: { 
               bsonType: "string", 
               description: "une chaîne" 
            },
            auteur: { 
               bsonType: "string", 
               description: "une chaîne" 
            },
            vues: { 
               bsonType: "int", 
               description: "un entier" }
         }
      }
   }
});

db.posts.insertMany([
    { titre: "Docker Docs", auteur: "Alice", vues: NumberInt(120) },
    { titre: "MongoDB Info", auteur: "Bob", vues: NumberInt(85) },
    { titre: "Cyber", auteur: "Charlie", vues: NumberInt(300) },
    { titre: "NoSQL", auteur: "Alice", vues: NumberInt(45) },
    { titre: "Azure", auteur: "Eve", vues: NumberInt(150) }
]);
