from typing import List

class TextChunker:
    """
    Splits long Amharic text into safe character lengths to prevent memory spikes
    and audio degradation over multi-sentence paragraphs.
    """
    
    @staticmethod
    def chunk_amharic_text(text: str, max_chars: int = 120) -> List[str]:
        delimiters = ['።', '?', '!', '\n', ';']
        for d in delimiters:
            text = text.replace(d, f"{d}|")
        
        raw_statements = text.split('|')
        chunks = []
        current_chunk = ""

        for stmt in raw_statements:
            stmt_clean = stmt.strip()
            if not stmt_clean:
                continue
                
            if len(current_chunk) + len(stmt_clean) + 1 <= max_chars:
                current_chunk = f"{current_chunk} {stmt_clean}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = stmt_clean

        if current_chunk:
            chunks.append(current_chunk)

        return chunks