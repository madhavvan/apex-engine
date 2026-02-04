// src/db.rs
use sqlx::{sqlite::SqlitePoolOptions, Pool, Sqlite, Row};
use crate::index::Document;
use anyhow::Result;

// This struct manages the connection to the database
#[derive(Clone)]
pub struct Database {
    pool: Pool<Sqlite>,
}

impl Database {
    // 1. Connect to the DB (and create the file if missing)
    pub async fn init() -> Result<Self> {
        let db_url = "sqlite:apex.db?mode=rwc"; // mode=rwc means Read/Write/Create
        
        let pool = SqlitePoolOptions::new()
            .max_connections(5)
            .connect(db_url)
            .await?;

        // 2. Create the Table if it doesn't exist
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                vector BLOB NOT NULL,
                content TEXT NOT NULL,
                url TEXT NOT NULL
            );
            "#
        )
        .execute(&pool)
        .await?;

        Ok(Database { pool })
    }

    // 3. Save a Document to the DB
    pub async fn add(&self, doc: &Document) -> Result<()> {
        // We store the vector as JSON bytes in the DB
        let vector_json = serde_json::to_string(&doc.vector)?;

        sqlx::query(
            "INSERT OR REPLACE INTO documents (id, vector, content, url) VALUES (?, ?, ?, ?)"
        )
        .bind(&doc.id)
        .bind(vector_json)
        .bind(&doc.content)
        .bind(&doc.url)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    // 4. Load ALL Documents (Used on Startup)
    pub async fn get_all(&self) -> Result<Vec<Document>> {
        let rows = sqlx::query("SELECT id, vector, content, url FROM documents")
            .fetch_all(&self.pool)
            .await?;

        let mut docs = Vec::new();
        for row in rows {
            // Convert the stored JSON blob back into a Vec<f32>
            let vector_str: String = row.get("vector");
            let vector: Vec<f32> = serde_json::from_str(&vector_str)?;

            docs.push(Document {
                id: row.get("id"),
                content: row.get("content"),
                url: row.get("url"),
                vector,
            });
        }
        Ok(docs)
    }
}