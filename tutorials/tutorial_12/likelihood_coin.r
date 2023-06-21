#!/usr/bin/R
head <- 3
tail <- 17
p <- seq(0,1,by=0.001)
for (i in p){L <- c((p^head)*(1-p)^tail)}
maxL <- max(L)
indexL <- match(maxL,L)
best_p <- p[indexL]
#pdf("plot_2.pdf")
plot(p, L, xlab="P(Ca)", ylab="L", col="blue", frame=F, pch=16,cex=0.5)
text(0.8, maxL, paste("L =", maxL, "\n P(Ca) =", best_p))
#dev.off()

