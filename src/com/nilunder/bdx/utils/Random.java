package com.nilunder.bdx.utils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import javax.vecmath.Vector3f;

public class Random{

	private static java.util.Random R;

	public static <T> T choice(ArrayList<T> list){
		if (R == null){
			R = new java.util.Random();
		}
		return list.get(R.nextInt(list.size()));
	}

	@SafeVarargs
	public static <T> T choice(T... args) {
		if (R == null){
			R = new java.util.Random();
		}
		return args[R.nextInt(args.length)];
	}

	public static float random(){
		if (R == null){
			R = new java.util.Random();
		}
		return R.nextFloat();
	}
	
	public static void seed(long seed){
		if (R == null)
			R = new java.util.Random();
		
		R.setSeed(seed);
	}

	public static float random(float min, float max){
		return (min + (random() * (max - min)));
	}

	public static Vector3f direction(){
		Vector3f vec = vector();
		vec.normalize();
		if (vec.length() == 0)
			vec = new Vector3f(1, 0, 0);
		return vec;
	}

	public static Vector3f vector(){
		ArrayList<Integer> ints = new ArrayList<Integer>();
		ints.add(1);
		ints.add(-1);
		return new Vector3f(
				Random.random() * Random.choice(ints),
				Random.random() * Random.choice(ints),
				Random.random() * Random.choice(ints));
	}

	public static Color color(){
		return new Color(Random.random(0, 1),
				Random.random(0, 1),
				Random.random(0, 1),
				Random.random(0, 1));
	}

	public static <T> ArrayList<T> selection(int minNum, int maxNum, T[] args, boolean repeats) {

		ArrayList<T> out = new ArrayList<T>();

		ArrayList<T> interim = new ArrayList<T>();

		Collections.addAll(interim, args);

		for (int i = 0; i < Math.floor(random(minNum, maxNum + 1)); i++) {
			if (interim.size() == 0)
				break;
			T ch = choice(interim);
			if (!repeats)
				interim.remove(ch);
			out.add(ch);
		}

		return out;

	}

	public static <T> ArrayList<T> selection(int minNum, int maxNum, T[] args) {
		return selection(minNum, maxNum, args, false);
	}

	public static <T> ArrayList<T> selection(int num, T[] args) {
		return selection(num, num, args, false);
	}

	@SafeVarargs
	public static <T> ArrayList<T> selection(T... args) {
		return selection(1, args.length, args, false);
	}

	public static <T> ArrayList<T> selection(int minNum, int maxNum, List<T> args, boolean repeats) {

		ArrayList<T> out = new ArrayList<T>();

		ArrayList<T> interim = new ArrayList<T>();

		interim.addAll(args);

		for (int i = 0; i < Math.floor(random(minNum, maxNum + 1)); i++) {

			if (interim.size() == 0)
				break;
			T ch = choice(interim);
			if (!repeats)
				interim.remove(ch);
			out.add(ch);
		}

		return out;

	}

	public static <T> ArrayList<T> selection(int minNum, int maxNum, List<T> args) {
		return selection(minNum, maxNum, args, false);
	}

	public static <T> ArrayList<T> selection(int num, List<T> args) {
		return selection(num, num, args, false);
	}

	public static <T> ArrayList<T> selection(List<T> args) {
		return selection(1, args.size(), args, false);
	}

}
