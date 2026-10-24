use std::env;
fn main() {
    let args: Vec<String> = env::args().collect();
    let a: i32 = if args[2] == "MIN" { i32::MIN } else { args[2].parse().unwrap() };
    let b: i32 = args[3].parse().unwrap();
    match args[1].as_str() {
        "div" => println!("{}", a / b),
        "checked" => println!("{:?}", a.checked_div(b)),
        "wrapping" => { if b != 0 { println!("{}", a.wrapping_div(b)) } else { println!("(wrapping_div also panics on 0)") } }
        "f64" => println!("{}", (a as f64) / (b as f64)),
        _ => {}
    }
}
