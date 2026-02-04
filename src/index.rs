// src/index.rs
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use hnsw_rs::prelude::*;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Document {
    pub id: String,
    pub vector: Vec<f32>,
    pub content: String, 
    pub url: String,
}

pub struct InMemoryIndex {
    // FIX 1: We added 'static here to tell Rust this lives forever
    pub hnsw: Hnsw<'static, f32, DistCosine>, 
    pub data_map: HashMap<usize, Document>,
    pub current_id: usize,
}

impl InMemoryIndex {
    pub fn new() -> Self {
        let max_elements = 100_000;
        let max_neighbors = 24;      // Typically 16-64
        let max_layers = 16;         // Typically 16
        let ef_construction = 200;
        
        // FIX 2: We updated the type definition here too
        let hnsw: Hnsw<'static, f32, DistCosine> = Hnsw::new(
            max_neighbors, 
            max_elements, 
            max_layers, 
            ef_construction, 
            DistCosine
        );
        
        InMemoryIndex { 
            hnsw, 
            data_map: HashMap::new(),
            current_id: 0,
        }
    }

    pub fn add(&mut self, doc: Document) {
        // We pass the vector and ID as a Tuple: (vector, id)
        self.hnsw.insert((&doc.vector, self.current_id));
        
        self.data_map.insert(self.current_id, doc);
        self.current_id += 1;
    }

    pub fn search(&self, query_vector: &[f32], top_k: usize) -> Vec<(Document, f32)> {
        let raw_results = self.hnsw.search(query_vector, top_k, 30);
        
        let mut results = Vec::new();

        for neighbor in raw_results {
            if let Some(doc) = self.data_map.get(&neighbor.d_id) {
                // Convert distance to similarity
                let similarity = 1.0 - neighbor.distance; 
                results.push((doc.clone(), similarity));
            }
        }
        
        results
    }
}