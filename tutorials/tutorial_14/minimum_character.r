#!/usr/bin/R
e <- sum(1/factorial(0:100))
VBt <- .95
t <- seq(3,100,by=1)
for (i in t){
r <- c(round((t-2) - (t-2)*e^(log(1-VBt, e)/(t-2)),0))
#R <- c(R,r)
}
#pdf("plot_3.pdf")
plot(t, r, xlab="N taxa", ylab="r", col="blue", frame=F, pch=16,cex=0.5)
#dev.off()


