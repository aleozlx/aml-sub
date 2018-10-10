extern crate clap;
use clap::{Arg, App, SubCommand};

fn main() {
    let matches = App::new("aml-sub")
        .version("1.0")
        .author("Alex Yang <zy5f9@mail.missouri.edu>")
        .about("Applied Machine Learning job submission")
        .arg(Arg::with_name("INPUT")
            .help("Input file")
            .required(true)
            .index(1))
        .get_matches();
}

