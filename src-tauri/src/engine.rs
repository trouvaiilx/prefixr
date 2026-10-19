use rand::seq::SliceRandom;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::cmp::Reverse;
use std::collections::HashSet;
use std::fs;
use std::path::Path;
use std::time::Instant;

const DEFAULT_WORDLIST: &str = include_str!("../../merged_english.txt");
const DEFAULT_WORDLIST_NAME: &str = "merged_english.txt";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SearchMode {
    Prefix,
    Suffix,
    Contains,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SortOrder {
    Shortest,
    Random,
    Longest,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MatchItem {
    pub word: String,
    pub match_start: usize,
    pub match_len: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SearchResponse {
    pub matches: Vec<MatchItem>,
    pub total_matches: usize,
    pub elapsed_us: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EngineStats {
    pub word_count: usize,
    pub used_count: usize,
    pub wordlist_name: String,
    pub is_custom_wordlist: bool,
}

pub struct DictionaryEngine {
    /// Lexicographically sorted unique lowercase words.
    words: Vec<String>,
    /// Reversed words paired with their index in `words`, sorted lexicographically by reversed word.
    reversed_words: Vec<(String, usize)>,
    /// Lowercase words marked as used during the current session.
    used_words: HashSet<String>,
    /// Display name of the currently loaded wordlist.
    wordlist_name: String,
    /// True if loaded from an external user-selected file.
    is_custom_wordlist: bool,
}

impl Default for DictionaryEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl DictionaryEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            words: Vec::new(),
            reversed_words: Vec::new(),
            used_words: HashSet::new(),
            wordlist_name: DEFAULT_WORDLIST_NAME.to_string(),
            is_custom_wordlist: false,
        };
        engine.load_from_str(DEFAULT_WORDLIST, DEFAULT_WORDLIST_NAME.to_string(), false);
        engine
    }

    pub fn from_str_custom(content: &str, name: &str) -> Self {
        let mut engine = Self {
            words: Vec::new(),
            reversed_words: Vec::new(),
            used_words: HashSet::new(),
            wordlist_name: name.to_string(),
            is_custom_wordlist: true,
        };
        engine.load_from_str(content, name.to_string(), true);
        engine
    }

    pub fn load_default(&mut self) {
        self.load_from_str(DEFAULT_WORDLIST, DEFAULT_WORDLIST_NAME.to_string(), false);
    }

    pub fn load_from_file(&mut self, path: &Path) -> Result<EngineStats, String> {
        let raw = fs::read_to_string(path)
            .map_err(|e| format!("Failed to read {}: {}", path.display(), e))?;
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("custom.txt")
            .to_string();
        self.load_from_str(&raw, name, true);
        Ok(self.stats())
    }

    pub fn load_from_str(&mut self, raw_text: &str, name: String, is_custom: bool) {
        let mut words: Vec<String> = raw_text
            .lines()
            .map(|l| l.trim().to_lowercase())
            .filter(|w| !w.is_empty())
            .collect();

        words.par_sort_unstable();
        words.dedup();

        let mut reversed_words: Vec<(String, usize)> = words
            .par_iter()
            .enumerate()
            .map(|(idx, w)| (w.chars().rev().collect::<String>(), idx))
            .collect();

        reversed_words.par_sort_unstable_by(|a, b| a.0.cmp(&b.0));

        self.words = words;
        self.reversed_words = reversed_words;
        self.used_words.clear();
        self.wordlist_name = name;
        self.is_custom_wordlist = is_custom;
    }

    pub fn search(
        &self,
        query: &str,
        mode: SearchMode,
        sort_order: SortOrder,
        max_results: usize,
    ) -> SearchResponse {
        let start = Instant::now();
        let q = query.trim().to_lowercase();

        if q.is_empty() || self.words.is_empty() || max_results == 0 {
            return SearchResponse {
                matches: Vec::new(),
                total_matches: 0,
                elapsed_us: start.elapsed().as_micros() as u64,
            };
        }

        let q_char_len = q.chars().count();

        let mut candidates: Vec<&str> = match mode {
            SearchMode::Prefix => {
                let lo = self.words.partition_point(|w| w.as_str() < q.as_str());
                let count = self.words[lo..].partition_point(|w| w.starts_with(&q));
                let slice = &self.words[lo..lo + count];
                if self.used_words.is_empty() {
                    slice.iter().map(|s| s.as_str()).collect()
                } else {
                    slice
                        .iter()
                        .filter(|w| !self.used_words.contains(w.as_str()))
                        .map(|s| s.as_str())
                        .collect()
                }
            }
            SearchMode::Suffix => {
                let rev_q: String = q.chars().rev().collect();
                let lo = self
                    .reversed_words
                    .partition_point(|(rw, _)| rw.as_str() < rev_q.as_str());
                let count = self.reversed_words[lo..]
                    .partition_point(|(rw, _)| rw.starts_with(&rev_q));
                let slice = &self.reversed_words[lo..lo + count];
                if self.used_words.is_empty() {
                    slice
                        .iter()
                        .map(|(_, idx)| self.words[*idx].as_str())
                        .collect()
                } else {
                    slice
                        .iter()
                        .map(|(_, idx)| self.words[*idx].as_str())
                        .filter(|w| !self.used_words.contains(*w))
                        .collect()
                }
            }
            SearchMode::Contains => {
                if self.used_words.is_empty() {
                    self.words
                        .par_iter()
                        .filter(|w| w.contains(&q))
                        .map(|s| s.as_str())
                        .collect()
                } else {
                    self.words
                        .par_iter()
                        .filter(|w| w.contains(&q) && !self.used_words.contains(w.as_str()))
                        .map(|s| s.as_str())
                        .collect()
                }
            }
        };

        let total_matches = candidates.len();
        if candidates.is_empty() {
            return SearchResponse {
                matches: Vec::new(),
                total_matches: 0,
                elapsed_us: start.elapsed().as_micros() as u64,
            };
        }

        let selected: Vec<&str> = match sort_order {
            SortOrder::Shortest => {
                candidates.sort_by_key(|w| (w.len(), *w));
                candidates.into_iter().take(max_results).collect()
            }
            SortOrder::Longest => {
                candidates.sort_by_key(|w| (Reverse(w.len()), *w));
                candidates.into_iter().take(max_results).collect()
            }
            SortOrder::Random => {
                let mut rng = rand::thread_rng();
                let amount = max_results.min(candidates.len());
                let (shuffled, _) = candidates.partial_shuffle(&mut rng, amount);
                shuffled.to_vec()
            }
        };

        let matches = selected
            .into_iter()
            .map(|word| {
                let match_start = match mode {
                    SearchMode::Prefix => 0,
                    SearchMode::Suffix => word.chars().count().saturating_sub(q_char_len),
                    SearchMode::Contains => word
                        .find(&q)
                        .map(|byte_idx| word[..byte_idx].chars().count())
                        .unwrap_or(0),
                };
                MatchItem {
                    word: word.to_string(),
                    match_start,
                    match_len: q_char_len,
                }
            })
            .collect();

        SearchResponse {
            matches,
            total_matches,
            elapsed_us: start.elapsed().as_micros() as u64,
        }
    }

    pub fn mark_used(&mut self, word: &str) -> EngineStats {
        let normalized = word.trim().to_lowercase();
        if !normalized.is_empty() {
            self.used_words.insert(normalized);
        }
        self.stats()
    }

    pub fn reset_used(&mut self) -> EngineStats {
        self.used_words.clear();
        self.stats()
    }

    pub fn stats(&self) -> EngineStats {
        EngineStats {
            word_count: self.words.len(),
            used_count: self.used_words.len(),
            wordlist_name: self.wordlist_name.clone(),
            is_custom_wordlist: self.is_custom_wordlist,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE_WORDS: &str = "
        preach
        precise
        precisely
        prepare
        prefer
        apple
        application
        applying
        running
        jumping
        swimming
        archipelago
        monarch
        searching
    ";

    #[test]
    fn test_prefix_search_and_sort() {
        let engine = DictionaryEngine::from_str_custom(SAMPLE_WORDS, "sample.txt");
        assert_eq!(engine.stats().word_count, 14);

        let res_short = engine.search("pre", SearchMode::Prefix, SortOrder::Shortest, 10);
        assert_eq!(res_short.total_matches, 5);
        assert_eq!(res_short.matches[0].word, "preach");
        assert_eq!(res_short.matches[0].match_start, 0);
        assert_eq!(res_short.matches[0].match_len, 3);
        assert_eq!(res_short.matches.last().unwrap().word, "precisely");

        let res_long = engine.search("pre", SearchMode::Prefix, SortOrder::Longest, 10);
        assert_eq!(res_long.matches[0].word, "precisely");
    }

    #[test]
    fn test_suffix_search() {
        let engine = DictionaryEngine::from_str_custom(SAMPLE_WORDS, "sample.txt");
        let res = engine.search("ing", SearchMode::Suffix, SortOrder::Shortest, 10);
        assert_eq!(res.total_matches, 5);
        let words: Vec<&str> = res.matches.iter().map(|m| m.word.as_str()).collect();
        assert_eq!(
            words,
            vec!["jumping", "running", "applying", "swimming", "searching"]
        );
        // Check suffix match_start for "jumping" (7 chars - 3 = 4)
        assert_eq!(res.matches[0].match_start, 4);
        assert_eq!(res.matches[0].match_len, 3);
    }

    #[test]
    fn test_contains_search() {
        let engine = DictionaryEngine::from_str_custom(SAMPLE_WORDS, "sample.txt");
        let res = engine.search("arch", SearchMode::Contains, SortOrder::Shortest, 10);
        assert_eq!(res.total_matches, 3);
        let words: Vec<&str> = res.matches.iter().map(|m| m.word.as_str()).collect();
        assert_eq!(words, vec!["monarch", "searching", "archipelago"]);
        // "monarch" -> "arch" starts at index 3
        assert_eq!(res.matches[0].match_start, 3);
        assert_eq!(res.matches[0].match_len, 4);
    }

    #[test]
    fn test_used_words_filtering() {
        let mut engine = DictionaryEngine::from_str_custom(SAMPLE_WORDS, "sample.txt");
        engine.mark_used("preach");
        assert_eq!(engine.stats().used_count, 1);

        let res = engine.search("pre", SearchMode::Prefix, SortOrder::Shortest, 10);
        assert_eq!(res.total_matches, 4);
        assert!(res.matches.iter().all(|m| m.word != "preach"));

        engine.reset_used();
        assert_eq!(engine.stats().used_count, 0);
        let res_after = engine.search("pre", SearchMode::Prefix, SortOrder::Shortest, 10);
        assert_eq!(res_after.total_matches, 5);
    }

    #[test]
    fn test_default_merged_english_dictionary() {
        let engine = DictionaryEngine::new();
        assert!(engine.stats().word_count > 400_000);
        assert_eq!(engine.stats().wordlist_name, "merged_english.txt");

        let prefix_res = engine.search("affix", SearchMode::Prefix, SortOrder::Shortest, 25);
        assert!(!prefix_res.matches.is_empty());
        assert!(prefix_res.matches.iter().all(|m| m.word.starts_with("affix")));

        let suffix_res = engine.search("ology", SearchMode::Suffix, SortOrder::Shortest, 25);
        assert!(!suffix_res.matches.is_empty());
        assert!(suffix_res.matches.iter().all(|m| m.word.ends_with("ology")));

        let contains_res = engine.search("zyz", SearchMode::Contains, SortOrder::Random, 25);
        assert!(!contains_res.matches.is_empty());
        assert!(contains_res.matches.iter().all(|m| m.word.contains("zyz")));
    }
}
