library(VennDiagram);
futile.logger::flog.threshold(futile.logger::ERROR, name = "VennDiagramLogger")
args = commandArgs(trailingOnly=TRUE)

input_dir = args[1]

filename = paste0(input_dir, "/feature.csv")
f_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/cadd.csv")
c_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/boqa.csv")
b_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/phenomize.csv")
p_data = read.csv(filename, header=FALSE, sep=",")[,1]

file_dir = paste0(args[2], "/")
dir.create(file.path(".", file_dir), showWarnings = FALSE)

name_list = c("FM", "Boqa", "Phenomize")
data_list = list()
data_list[length(data_list) + 1] = list(f_data)
data_list[length(data_list) + 1] = list(b_data)
data_list[length(data_list) + 1] = list(p_data)
index_list = c(1:3)

for(i in 1:3){
	for(j in index_list[-i]){
		diff_set = setdiff(data_list[[i]], data_list[[j]])
		tmp = strsplit(diff_set, ",")
		sample_list = c()
		gene_list = c() 
		
		for(index in 1:length(tmp)){
			sample_list = c(sample_list, tmp[[index]][1])
			gene_list = c(gene_list, tmp[[index]][2])
		}
		
		out = cbind(sample_list, gene_list)
		filename = paste0(file_dir, name_list[i], "_without_", name_list[j], ".csv")
		write.csv(out, file=filename)
	}
}

index_list = list()
index_list[length(index_list) + 1] = list(c(2, 3))
index_list[length(index_list) + 1] = list(c(1, 3))
index_list[length(index_list) + 1] = list(c(1, 2))
for(i in 1:3){
	diff_set = setdiff(intersect(data_list[[index_list[[i]][1]]], data_list[[index_list[[i]][2]]]), data_list[[i]])
	print(diff_set)
	tmp = strsplit(diff_set, ",")
	sample_list = c()
	gene_list = c() 
	for(index in 1:length(tmp)){
		sample_list = c(sample_list, tmp[[index]][1])
		gene_list = c(gene_list, tmp[[index]][2])
	}
	
	out = cbind(sample_list, gene_list)
	filename = paste0(file_dir, name_list[index_list[[i]][1]], "_", name_list[index_list[[i]][2]] ,"_without_", name_list[i], ".csv")
	write.csv(out, file=filename)
}


venn.diagram(
	x = list(
		FM = f_data,
		boqa = b_data,
		penomize = p_data
		),
	filename = paste0(file_dir, "Venn-3sets.png"),
	height = 3000, width = 3600,
	col = "black",
	lty = "dotted",
	lwd = 4,
	fill = c("green", "yellow", "darkorchid1"),
	alpha = 0.50,
	label.col = c("orange", "white", "darkorchid4", "white", "darkblue", "white", "white"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("darkgreen", "orange", "darkorchid4"),
	cat.cex = 2.5,
	cat.fontfamily = "serif",
	imagetype = "png"
	);
# Figure 1D
venn.diagram(
	x = list(
		gestalt = f_data,
		CADD = c_data,
		boqa = b_data,
		penomize = p_data
		),
	filename = paste0(file_dir, "Venn-4sets.png"),
	height = 3000, width = 3600,
	col = "black",
	lty = "dotted",
	lwd = 4,
	fill = c("cornflowerblue", "green", "yellow", "darkorchid1"),
	alpha = 0.50,
	label.col = c("orange", "white", "darkorchid4", "white", "white", "white", "white", "white", "darkblue", "white", "white", "white", "white", "darkgreen", "white"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("darkblue", "darkgreen", "orange", "darkorchid4"),
	cat.cex = 2.5,
	cat.fontfamily = "serif",
	imagetype = "png"
	);


print("pathogenic gene")
filename = paste0(input_dir, "/pa_feature.csv")
f_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/pa_cadd.csv")
c_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/pa_boqa.csv")
b_data = read.csv(filename, header=FALSE, sep=",")[,1]
filename = paste0(input_dir, "/pa_phenomize.csv")
p_data = read.csv(filename, header=FALSE, sep=",")[,1]

name_list = c("FM", "Boqa", "Phenomize")
data_list = list()
data_list[length(data_list) + 1] = list(f_data)
data_list[length(data_list) + 1] = list(b_data)
data_list[length(data_list) + 1] = list(p_data)
index_list = c(1:3)

for(i in 1:3){
	for(j in index_list[-i]){
		diff_set = setdiff(data_list[[i]], data_list[[j]])
		print(diff_set)
		tmp = strsplit(diff_set, ",")
		print(tmp)
		sample_list = c()
		gene_list = c() 
		
		if(length(tmp) > 0){
			for(index in 1:length(tmp)){
				sample_list = c(sample_list, tmp[[index]][1])
				gene_list = c(gene_list, tmp[[index]][2])
			}
		}
		out = cbind(sample_list, gene_list)
		filename = paste0(file_dir, "pa_", name_list[i], "_without_", name_list[j], ".csv")
		write.csv(out, file=filename)
	}
}

print("pathogenic gene-2")
index_list = list()
index_list[length(index_list) + 1] = list(c(2, 3))
index_list[length(index_list) + 1] = list(c(1, 3))
index_list[length(index_list) + 1] = list(c(1, 2))
for(i in 1:3){
	diff_set = setdiff(intersect(data_list[[index_list[[i]][1]]], data_list[[index_list[[i]][2]]]), data_list[[i]])
	print(diff_set)
	tmp = strsplit(diff_set, ",")
	sample_list = c()
	gene_list = c() 
	if(length(tmp) > 0){
		for(index in 1:length(tmp)){
			sample_list = c(sample_list, tmp[[index]][1])
			gene_list = c(gene_list, tmp[[index]][2])
		}
	}
	
	out = cbind(sample_list, gene_list)
	filename = paste0(file_dir, "pa_", name_list[index_list[[i]][1]], "_", name_list[index_list[[i]][2]] ,"_without_", name_list[i], ".csv")
	write.csv(out, file=filename)
}
venn.diagram(
	x = list(
		FM = f_data,
		boqa = b_data,
		penomize = p_data
		),
	filename = paste0(file_dir, "Venn-3sets_pa.png"),
	height = 3000, width = 3600,
	col = "black",
	lty = "dotted",
	lwd = 4,
	fill = c("green", "yellow", "darkorchid1"),
	alpha = 0.50,
	label.col = c("orange", "white", "darkorchid4", "white", "darkblue", "white", "white"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("darkgreen", "orange", "darkorchid4"),
	cat.cex = 2.5,
	cat.fontfamily = "serif",
	imagetype = "png"
	);
# Figure 1D
venn.diagram(
	x = list(
		gestalt = f_data,
		CADD = c_data,
		boqa = b_data,
		penomize = p_data
		),
	filename = paste0(file_dir, "Venn-4sets_pa.png"),
	height = 3000, width = 3600,
	col = "black",
	lty = "dotted",
	lwd = 4,
	fill = c("cornflowerblue", "green", "yellow", "darkorchid1"),
	alpha = 0.50,
	label.col = c("orange", "white", "darkorchid4", "white", "white", "white", "white", "white", "darkblue", "white", "white", "white", "white", "darkgreen", "white"),
	cex = 2.5,
	fontfamily = "serif",
	fontface = "bold",
	cat.col = c("darkblue", "darkgreen", "orange", "darkorchid4"),
	cat.cex = 2.5,
	cat.fontfamily = "serif",
	imagetype = "png"
	);
