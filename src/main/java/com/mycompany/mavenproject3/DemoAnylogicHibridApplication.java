package com.mycompany.mavenproject3;

import com.fasterxml.jackson.databind.ObjectMapper;
import modelVessel.IterationStats;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.stream.Collectors;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class, HibernateJpaAutoConfiguration.class})
public class DemoAnylogicHibridApplication {

    //public static Hashtable<Iteration, IterationStats> iterationsMap = new Hashtable<>();
    public static ConcurrentLinkedQueue<Iteration> iterationsQueue = new ConcurrentLinkedQueue();
    volatile public static List<String> iterationString = new ArrayList<>();
    volatile public static Integer iterationQtt = 0;
    static Path configRanFile = Paths.get("executedIterations.txt");
    static Path statsFile = Paths.get("stats.txt");


    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        SpringApplication.run(DemoAnylogicHibridApplication.class, args);
        System.out.println("AnyLogic Simulation API Server Started");
        System.out.println("Available endpoints:");
        System.out.println("  POST /api/simulation/run - Run simulation with parameters");
        System.out.println("  GET  /api/simulation/health - Health check");
        System.out.println("  GET  /api/simulation/results/{id} - Get specific results");
        System.out.println("  GET  /api/simulation/all-results - Get all results");
        System.out.println("  DELETE /api/simulation/clear-cache - Clear results cache");
        System.out.println("Server is ready to accept requests from Python optimizer...");
    }

    public static List<Iteration> getExistingIterations() throws IOException, ClassNotFoundException {
        File file = configRanFile.toFile();
        List<Iteration> executedIterations = new ArrayList<>();

        if(file.exists()) {
            /*List<String> serializedIterationList = Files.readAllLines(configRanFile);

            for (String serializedIteration : serializedIterationList) {
                System.out.println("Serialized iteration: "+ serializedIteration);
                byte b[] = serializedIteration.getBytes();
                System.out.println("Bytes " + b);
                ByteArrayInputStream bi = new ByteArrayInputStream(b);
                ObjectInputStream si = new ObjectInputStream(bi);
                Iteration iteration = (Iteration) si.readObject();
                executedIterations.add(iteration);
            }*/

            List<String> serializedIterationList = Files.readAllLines(configRanFile);

            for (String serializedIteration : serializedIterationList) {

                ObjectMapper objectMapper = new ObjectMapper();
                Iteration iteration = objectMapper.readValue(serializedIteration, Iteration.class);

                executedIterations.add(iteration);
            }

        }

        return executedIterations;
    }

}
