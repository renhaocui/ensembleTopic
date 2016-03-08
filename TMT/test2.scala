import scalanlp.io._;
import scalanlp.stage._;
import scalanlp.stage.text._;
import scalanlp.text.tokenize._;
import scalanlp.pipes.Pipes.global._;

import edu.stanford.nlp.tmt.stage._;
import edu.stanford.nlp.tmt.model.lda._;
import edu.stanford.nlp.tmt.model.llda._;

val modelPath = file("TMT Snapshots");

println("Loading "+modelPath);
val model = LoadCVB0LDA(modelPath);

val source = CSVFile("TMT\\LDAFormatTrain.csv");

val text = {
  source ~>                              // read from the source file
  Column(2) ~>                           // select column containing text
  TokenizeWith(model.tokenizer.get)      // tokenize with existing model's tokenizer
}

// Base name of output files to generate
val output = file(modelPath, source.meta[java.io.File].getName.replaceAll(".csv",""));

// turn the text into a dataset ready to be used with LDA
val dataset = LDADataset(text, termIndex = model.termIndex);

println("Writing document distributions to "+output+"-document-topic-distributions.csv");
val perDocTopicDistributions = InferCVB0DocumentTopicDistributions(model, dataset);
CSVFile(output+"-document-topic-distributuions.csv").write(perDocTopicDistributions);
/*
println("Writing topic usage to "+output+"-usage.csv");
val usage = QueryTopicUsage(model, dataset, perDocTopicDistributions);
CSVFile(output+"-usage.csv").write(usage);
*/
println("Estimating per-doc per-word topic distributions");
val perDocWordTopicDistributions = EstimatePerWordTopicDistributions(
  model, dataset, perDocTopicDistributions);

println("Writing top terms to "+output+"-top-terms.csv");
val topTerms = QueryTopTerms(model, dataset, perDocWordTopicDistributions, numTopTerms=50);
CSVFile(output+"-top-terms.csv").write(topTerms);

