public class Divide {
    public static void main(String[] args) {
        int a = Integer.parseInt(args[1]), b = Integer.parseInt(args[2]);
        double x = Double.parseDouble(args[1]), y = Double.parseDouble(args[2]);
        try {
            if (args[0].equals("int")) System.out.println(a / b);
            else if (args[0].equals("min")) System.out.println(Integer.MIN_VALUE / b);
            else System.out.println(x / y);
        } catch (ArithmeticException e) { System.out.println("ArithmeticException: " + e.getMessage()); }
    }
}
