// src/main.rs
mod math;
mod index;
mod db; 

use actix_files as fs;
use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use index::{InMemoryIndex, Document};
use db::Database;
use serde::Deserialize;
use std::sync::{Arc, RwLock};

struct AppState {
    index: Arc<RwLock<InMemoryIndex>>, // The fast RAM search
    db: Database,                      // The persistent storage
}

#[derive(Deserialize)]
struct SearchQuery {
    vector: Vec<f32>,
    k: usize,
}

// --- ADD DATA (Updated) ---
async fn add_vector(data: web::Data<AppState>, doc: web::Json<Document>) -> impl Responder {
    let new_doc = doc.into_inner();
    
    // 1. Save to Real DB (Disk) - Async/Await
    if let Err(e) = data.db.add(&new_doc).await {
        return HttpResponse::InternalServerError().body(format!("DB Error: {}", e));
    }

    // 2. Update RAM Index (Memory)
    let mut index = data.index.write().unwrap(); 
    index.add(new_doc);
    
    HttpResponse::Ok().body("Vector saved to Database & Index")
}

// --- SEARCH DATA (Same as before) ---
async fn search_vectors(data: web::Data<AppState>, query: web::Json<SearchQuery>) -> impl Responder {
    let index = data.index.read().unwrap();
    let results = index.search(&query.vector, query.k);
    HttpResponse::Ok().json(results)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // 1. Connect to Database
    println!("Connecting to SQLite Database...");
    let db = match Database::init().await {
        Ok(d) => d,
        Err(e) => {
            eprintln!("Failed to connect to DB: {}", e);
            return Ok(());
        }
    };

    // 2. Load Existing Data from Disk
    println!("Loading vectors from Disk...");
    let saved_docs = db.get_all().await.unwrap();
    let count = saved_docs.len();

    let mut memory_index = InMemoryIndex::new();
    for doc in saved_docs {
        memory_index.add(doc);
    }
    
    let index_ref = Arc::new(RwLock::new(memory_index));
    println!("✅ Apex Engine ready! Loaded {} vectors.", count);

    // 3. Start Server
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(AppState {
                index: index_ref.clone(),
                db: db.clone(),
            }))
            .route("/add", web::post().to(add_vector))
            .route("/search", web::post().to(search_vectors))
            .service(fs::Files::new("/", "./static").index_file("index.html"))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}