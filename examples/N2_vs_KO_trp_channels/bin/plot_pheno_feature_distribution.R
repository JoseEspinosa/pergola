#!/usr/bin/env Rscript

#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################
### Jose Espinosa-Carrasco NPMMD/CB-CRG Group. May 2016                   ###
#############################################################################
### Mean values for each group of worms                                   ###
### Using bed files raw data intercepted with the motion                  ### 
#############################################################################

# To use this script in ant first export this:
# export R_LIBS="/software/R/packages"

##Getting HOME directory 
home <- Sys.getenv("HOME")

### Execution example
## Rscript plot_speed_motion_mean.R --bed_file="bed_file"

library(ggplot2)

# Loading params plot:
source("https://raw.githubusercontent.com/cbcrg/mwm/master/lib/R/plot_param_public.R")

#####################
### VARIABLES
#Reading arguments
args <- commandArgs (TRUE) #if not it doesn't start to count correctly

## Default setting when no arguments passed
if ( length(args) < 1) {
  args <- c("--help")
}

## Help section
if("--help" %in% args) {
  cat("
      plot_speed_motion_mean.R
      
      Arguments:
      --bed_file=concat_bed_file     - character      
      --help                         - print this text
      
      Example:
      ./plot_speed_motion_mean.R --bed_file=\"path_to_file\" \n")
  
  q (save="no")
}

# Use to parse arguments beginning by --
parseArgs <- function(x) 
{
  strsplit (sub ("^--", "", x), "=")
}

#Parsing arguments
argsDF <- as.data.frame (do.call("rbind", parseArgs(args)))
argsL <- as.list (as.character(argsDF$V2))
names (argsL) <- argsDF$V1

# All arguments are mandatory
{
  if (is.null (argsL$bed_file)) 
  {
    stop ("[FATAL]: bed_file arg is mandatory")
  }
  else
  {
    bed_file <- argsL$bed_file
  }
}

# bed_file<- "/Users/jespinosa/git/pergola/examples/N2_vs_KO_trp_channels/work/b3/13da3ae83a8ed9ac189b2b98691790/575_JU440.tail_motion.forward.bed"
# bed_file<- "/Users/jespinosa/git/pergola/examples/N2_vs_KO_trp_channels/work/ab/5caa9eac6c274c2fe0ae2ca65f7452/N2.crawling.forward.bed"
# info = file.info(bed_file)
# {  
#   if (info$size == 0) { 
#     df_bed <- data.frame (chr="chr1", start=0, end=0, data_type=0, value=0, strand=0, s=0, e=0, color_code=0)
#   }
#   else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")
#          colnames (df_bed) <- c("chr", "start", "end", "data_type", "value", "strand", "s", "e", "color_code")         
#          #return (df)
#   }  
# }

info = file.info(bed_file)
{  
  if (info$size == 0) { 
    df_bed <- data.frame (chr="chr1", start=0, end=0, data_type=0, value=0, strand=0, s=0, e=0, color_code=0, body_part=0, direction=0)
  }
  else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")
         colnames (df_bed) <- c("chr", "start", "end", "data_type", "value", "strand", "s", "e", "color_code", "body_part", "direction")         
  }  
}

# We remove this fake rows they were included just to avoid last line of code above to crash
df_bed <- df_bed [!(df_bed$start == 0 & df_bed$end == 0), ]

name_file <- basename(bed_file)
name_out <- paste(name_file, ".png", sep="")

name_split <- strsplit (name_file, "\\." )

body_part <- name_split[[1]][2]
motion <- name_split[[1]][3]

# info = file.info(bed_file)
# {  
#   if (info$size == 0) { 
#     df_bed <- data.frame (chr="chr1", start=0, end=0, data_type=0, value=0, strand=0, s=0, e=0, color_code=0, body_part=0, direction=0)
#   }
#   else { df_bed <- read.csv(file=bed_file, header=F, sep="\t")
#          colnames (df_bed) <- c("chr", "start", "end", "data_type", "value", "strand", "s", "e", "color_code", "body_part", "direction")         
#   }  
# }

pheno_feature <- strsplit (name_file,  "\\.")[[1]][2]
units <- switch (pheno_feature, foraging_speed="Degrees/seconds", tail_motion="Degrees/seconds", crawling="Degrees", 'no units')

title_strain_pheno_dir <- gsub("_", " ", gsub ("\\.", " - ", gsub ("\\.bed", "", name_file)))

# many files of gk298 strain are annotated as ok298
title_strain_pheno_dir <- gsub ("ok298", "gk298", title_strain_pheno_dir)

size_strips <- 12
size_titles <- 13
size_axis <- 12
size_axis_ticks <- 10
# xmin <- -1000
# xmax <- 1000

df_bed$body_part <- gsub ("_", " ", df_bed$body_part)

ggplot(df_bed, aes(x=value)) + geom_density() +
  #scale_x_continuous (breaks=c(xmin, 0, xmax), limits=c(xmin-100, xmax+100)) +  
#   labs (title = paste(pattern_worm, motion, body_part, "\n", sep=" ")) +
  labs (title = paste(title_strain_pheno_dir, "\n", sep=" ")) +
  labs (x = paste("\n", units, sep=""), y = "Probability density\n") +  
  # theme (strip.text.x = element_text(size=size_strips, face="bold")) +
  theme (plot.title = element_text(size=size_titles)) + 
  theme (axis.title.x = element_text(size=size_axis)) +
  theme (axis.title.y = element_text(size=size_axis)) +
  theme (axis.text.x = element_text(size=size_axis_ticks)) +  
  theme (axis.text.y = element_text(size=size_axis_ticks)) +  
  theme (strip.background = element_blank()) 
  
ggsave (file=name_out)

### Developing mean plot

# http://www.sthda.com/english/wiki/print.php?id=180

# plotar uno encima de otro, el pequenyo encima y con los puntos
## gitter
# library(ggplot2)
# df <- ToothGrowth
# df$dose <- as.factor(df$dose)
# p <- ggplot(df, aes(x=dose, y=len)) + 
#   geom_dotplot(binaxis='y', stackdir='center')
# p
# # use geom_crossbar()
# # The function mean_sdl is used. mean_sdl computes the mean plus or minus a constant times the standard deviation.
# # In the R code below, the constant is specified using the argument mult (mult = 1). By default mult = 2.
# p + stat_summary(fun.data="mean_sdl", geom="crossbar", width = 0.5, mult=1)
#                  , mult=1, 
#                  geom="crossbar", width=0.5)
# ?stat_summary
