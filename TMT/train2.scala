import scalanlp.io._;
import scalanlp.stage._;
import scalanlp.stage.text._;
import scalanlp.text.tokenize._;
import scalanlp.pipes.Pipes.global._;

import edu.stanford.nlp.tmt.stage._;
import edu.stanford.nlp.tmt.model.lda._;
import edu.stanford.nlp.tmt.model.llda._;

val source = CSVFile("TMT\\LDAFormatTrain.csv");

val tokenizer = {
  SimpleEnglishTokenizer() ~>            // tokenize on space and punctuation
  CaseFolder() ~>                        // lowercase everything
  WordsAndNumbersOnlyFilter() ~>         // ignore non-words and non-numbers
  MinimumLengthFilter(1)                 // take terms with >=1 characters
}

val text = {
  source ~>                              // read from the source file
  Column(2) ~>                           // select column containing text
  TokenizeWith(tokenizer) ~>             // tokenize with tokenizer above
  TermCounter() ~>                       // collect counts (needed below)
  TermMinimumDocumentCountFilter(1) ~>   // filter terms in <1 docs
  TermDynamicStopListFilter(30000000) ~>       // filter out most common terms
  DocumentMinimumLengthFilter(3)         // take only docs with >=1 terms
}

val dataset = LDADataset(text);

// define the model parameters
val params = LDAModelParams(numTopics = 200, dataset = dataset, topicSmoothing = 0.01, termSmoothing = 0.01);

// Name of the output model folder to generate
val modelPath = file("TMT Snapshots");

// Trains the model, writing to the given output path
TrainCVB0LDA(params, dataset, output = modelPath, maxIterations = 1000);