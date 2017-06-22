library(ggplot2)
library(reshape2)
library(ggdendro)
library(grid)


args = commandArgs(trailingOnly=TRUE)
input_file = args[1]
output_dir = args[2]
data = read.csv(input_file, check.names = FALSE)
genenames = data[,1]
data = data[,-1]
rownames(data) = genenames
data = data[apply(data[,-1], 1, function(x) !all(x==0)),]
### We transpose matrix first, then scale the column. Column - Actual, Row - Predicted
data = t(data)
x <- as.matrix(scale(data))
#x = x[,-which(is.na(x[1,]))]

dd.col <- as.dendrogram(hclust(dist(x)))
col.ord <- order.dendrogram(dd.col)

dd.row <- as.dendrogram(hclust(dist(t(x))))
row.ord <- order.dendrogram(dd.row)

xx <- scale(data)[col.ord, row.ord]

xx_names <- attr(xx, "dimnames")
df <- as.data.frame(xx)
colnames(df) <- xx_names[[2]]
df$Sample <- xx_names[[1]]
df$Sample <- with(df, factor(Sample, levels=Sample, ordered=TRUE))

#quantile_range <- quantile(df, probs = seq(0, 1, 0.2))
mdf <- melt(df, id.vars="Sample")

ddata_x <- dendro_data(dd.row)
ddata_y <- dendro_data(dd.col)

### Set up a blank theme
theme_none <- theme(
	panel.grid.major = element_blank(),
	panel.grid.minor = element_blank(),
	panel.background = element_blank(),
	axis.title.x = element_text(colour=NA),
	axis.title.y = element_blank(),
	axis.text.x = element_blank(),
	axis.text.y = element_blank(),
	axis.line = element_blank()
	)

colnames(mdf)[2] = "Gene"

### Create plot components ###    
# Heatmap
p1 <- ggplot(mdf, aes(x=Gene, y=Sample)) + 
  geom_tile(aes(fill=value)) + scale_fill_gradient2(low="#FFFFFF", mid="#FDBB84", high="#E34A33") +
  theme(text = element_text(size=16), axis.text.x = element_text(angle=90, hjust=1)) +
  scale_x_discrete(position = "top") +
  scale_y_discrete(position = "right")
ptop <- p1 + theme( axis.text.x = element_text(color="black", size=14), axis.text.y = element_text(color="gray90", size=14))  + coord_cartesian(ylim = c(0,0))
# Dendrogram 1
p2 <- ggplot(segment(ddata_x)) + 
  geom_segment(aes(x=x, y=y, xend=xend, yend=yend)) + 
    theme_none + theme(axis.title.x=element_blank())

# Dendrogram 2
p3 <- ggplot(segment(ddata_y)) + 
  geom_segment(aes(x=x, y=y, xend=xend, yend=yend)) + 
    coord_flip() + theme_none


jpeg(paste0(output_dir, "/clustering_heatmap_gestalt.jpg"), width=4000, height=3600)
grid.newpage()
print(p1, vp=viewport(0.8, 0.8, x=0.4, y=0.4))
print(p2, vp=viewport(0.81, 0.2, x=0.375, y=0.9))
print(p3, vp=viewport(0.2, 0.84, x=0.9, y=0.39))
dev.off()
