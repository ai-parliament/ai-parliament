# Data Directory 📊

This directory contains data storage and management components for the AI Parliament system. It serves as the central location for persistent data, including vector databases, cached content, and other data artifacts.

## 📁 Structure

```
data/
├── 📄 README.md                    # This documentation
└── 📁 vector_db/                   # Vector database storage
    └── [FAISS index files]         # Generated vector database files
```

## 🗄️ Data Components

### Vector Database (`vector_db/`)

The vector database directory contains FAISS-based vector storage files:

**Purpose:**
- Store embeddings of political knowledge
- Enable semantic search capabilities
- Provide context for AI agents
- Cache Wikipedia and other external data

**Contents:**
- **Index Files**: FAISS index structures for fast similarity search
- **Metadata**: Associated metadata for stored vectors
- **Embeddings**: Vector representations of text content
- **Mappings**: ID-to-content mapping files

**File Types:**
- `.faiss` - FAISS index files
- `.pkl` - Pickled metadata and mappings
- `.json` - Configuration and metadata files
- `.txt` - Raw text content cache

## 🔧 Data Management

### Vector Database Operations

The vector database supports:
- **Indexing**: Adding new content to the database
- **Searching**: Finding similar content based on queries
- **Updating**: Modifying existing entries
- **Deletion**: Removing outdated content

### Data Sources

Data stored in the vector database comes from:
- **Wikipedia Articles**: Political party and politician information
- **Legislative Documents**: Sample legislation and policies
- **Historical Data**: Past political decisions and statements
- **User Content**: Custom party and politician definitions

## 🚀 Usage

### Accessing Vector Database

The vector database is accessed through the AI module:

```python
from ai.src.database.vector_db import VectorDatabase

# Initialize database
db = VectorDatabase(data_path="data/vector_db")

# Search for relevant content
results = db.search("climate change policy", top_k=5)

# Add new content
db.add_document("New policy document", metadata={"type": "policy"})
```

### Database Initialization

The vector database is automatically initialized when:
- First simulation is run
- Wikipedia data is cached
- Custom content is added

### Performance Optimization

For optimal performance:
- **Batch Operations**: Add multiple documents at once
- **Index Optimization**: Rebuild index periodically
- **Memory Management**: Monitor memory usage during operations
- **Disk Space**: Ensure adequate storage space

## 📈 Data Growth

### Storage Requirements

Expected storage growth:
- **Initial Setup**: ~100MB for basic Wikipedia cache
- **Full Cache**: ~1GB for comprehensive political data
- **User Data**: Variable based on custom content
- **Index Overhead**: ~20% additional space for FAISS indices

### Maintenance

Regular maintenance tasks:
- **Index Optimization**: Rebuild indices for better performance
- **Data Cleanup**: Remove outdated or unused content
- **Backup**: Regular backups of important data
- **Monitoring**: Track storage usage and performance

## 🔒 Data Security

### Privacy Considerations

- **No Personal Data**: Only public political information stored
- **Anonymization**: User-generated content anonymized
- **Access Control**: Database access through application only
- **Audit Trail**: Log all data access and modifications

### Backup Strategy

Recommended backup approach:
- **Regular Snapshots**: Daily backups of vector database
- **Version Control**: Track changes to data structure
- **Cloud Storage**: Backup to secure cloud storage
- **Recovery Testing**: Regular restore testing

## 🛠️ Configuration

### Environment Variables

Data-related configuration:
```env
# Vector database settings
VECTOR_DB_PATH=data/vector_db
VECTOR_DB_DIMENSION=1536
VECTOR_DB_INDEX_TYPE=IVF
VECTOR_DB_NLIST=100

# Cache settings
CACHE_SIZE_LIMIT=1GB
CACHE_TTL=86400  # 24 hours
```

### Database Settings

Vector database configuration:
- **Dimension**: 1536 (OpenAI embedding dimension)
- **Index Type**: IVF (Inverted File Index)
- **Distance Metric**: Cosine similarity
- **Batch Size**: 100 documents per batch

## 🧹 Data Cleanup

### Automated Cleanup

The system includes automated cleanup:
- **TTL Expiration**: Remove expired cache entries
- **Size Limits**: Enforce maximum database size
- **Duplicate Detection**: Remove duplicate content
- **Orphan Cleanup**: Remove unreferenced data

### Manual Cleanup

For manual cleanup:
```bash
# Clear all cached data
rm -rf data/vector_db/*

# Clear specific cache
rm -rf data/vector_db/wikipedia_cache/

# Rebuild index
python -c "from ai.src.database.vector_db import VectorDatabase; VectorDatabase().rebuild_index()"
```

## 📊 Monitoring

### Database Metrics

Key metrics to monitor:
- **Storage Usage**: Total disk space used
- **Index Size**: Size of FAISS indices
- **Query Performance**: Average search response time
- **Cache Hit Rate**: Percentage of cache hits vs misses

### Health Checks

Regular health checks:
- **Index Integrity**: Verify index files are not corrupted
- **Data Consistency**: Check metadata consistency
- **Performance**: Monitor query response times
- **Storage**: Check available disk space

## 🔄 Migration

### Data Migration

When upgrading:
1. **Backup Current Data**: Create full backup
2. **Export Metadata**: Save all metadata
3. **Rebuild Indices**: Create new indices with updated format
4. **Verify Integrity**: Ensure all data migrated correctly
5. **Update Configuration**: Adjust settings as needed

### Version Compatibility

- **Backward Compatibility**: Older data formats supported
- **Migration Scripts**: Automated migration tools available
- **Rollback Support**: Ability to revert to previous version
- **Testing**: Thorough testing before production migration

## 🐛 Troubleshooting

### Common Issues

1. **Index Corruption:**
   ```bash
   # Rebuild corrupted index
   python -c "from ai.src.database.vector_db import VectorDatabase; VectorDatabase().rebuild_index()"
   ```

2. **Out of Disk Space:**
   ```bash
   # Check disk usage
   du -sh data/vector_db/
   
   # Clean old cache
   find data/vector_db/ -type f -mtime +30 -delete
   ```

3. **Slow Queries:**
   - Check index optimization
   - Monitor system resources
   - Consider index rebuilding

### Performance Issues

For performance problems:
- **Memory Usage**: Monitor RAM consumption
- **Disk I/O**: Check disk read/write speeds
- **Index Size**: Consider index optimization
- **Query Complexity**: Simplify complex queries

## 📚 Further Reading

- [FAISS Documentation](https://faiss.ai/)
- [Vector Database Best Practices](https://www.pinecone.io/learn/vector-database/)
- [Embedding Strategies](https://platform.openai.com/docs/guides/embeddings)
- [Data Management Patterns](https://martinfowler.com/articles/data-mesh-principles.html)