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
        System.out.println("Initialized");
        List<Iteration> executedIterations = getExistingIterations();

        Integer skippedIterations = 0;

        for (Integer capacityOfMainConveyor = 800; capacityOfMainConveyor <= 1200; capacityOfMainConveyor += 200) {
            for (Integer quantityOfVagonsToSilageAtOnce = 8; quantityOfVagonsToSilageAtOnce <= 10; quantityOfVagonsToSilageAtOnce += 1) {
                for (Integer quantityOfVehicleDischargeStations = 2; quantityOfVehicleDischargeStations <= 4; quantityOfVehicleDischargeStations += 1) {
                    for (Integer numberOfVehicleSilages = 2; numberOfVehicleSilages <= 4; numberOfVehicleSilages += 1) {
                        for (Integer capacityOfVehicleSilage = 800; capacityOfVehicleSilage <= 1000; capacityOfVehicleSilage += 100) {
                            for (Integer quantityOfSilages = 17; quantityOfSilages <= 19; quantityOfSilages += 1) {
                                Iteration iteration = new Iteration();
                                iteration.setVarOfWork(3)
                                        .setCapacityOfMainConveyor(capacityOfMainConveyor)
                                        .setQuantityOfVagonsToSilageAtOnce(quantityOfVagonsToSilageAtOnce)
                                        .setQuantityOfVehicleDischargeStations(quantityOfVehicleDischargeStations)
                                        .setNumberOfVehicleSilages(numberOfVehicleSilages)
                                        .setCapacityOfVehicleSilages(capacityOfVehicleSilage)
                                        .setQuantityOfSilages(quantityOfSilages)
                                        .setYearsModelWorking(1);

                                if(!executedIterations.contains(iteration)) {
                                    iterationsQueue.add(iteration);
                                } else {
                                    System.out.println("Skipping iteration: " + iteration);
                                    skippedIterations++;
                                }
                            }
                        }
                    }
                }
            }
        }

        System.out.println("===== Iterations skipped in total: " + skippedIterations + " =====");


        iterationQtt = iterationsQueue.size();


        List<IterationCallable> callableList = iterationsQueue.stream().map(iteration -> new IterationCallable(configRanFile, statsFile, iteration)).toList();
        ConcurrentLinkedQueue<IterationCallable> callableQueue = new ConcurrentLinkedQueue();
        callableQueue.addAll(callableList);
        ExecutorService updateService = Executors.newFixedThreadPool(10);
        while(callableQueue.size() != 0) {
            System.out.println("Current queue size: " + callableQueue.size());

            Future<IterationStats> futureResult = updateService.submit(callableQueue.poll());
            IterationStats result = null;
            try {
                result = futureResult.get(5, TimeUnit.MINUTES);
            } catch (TimeoutException | ExecutionException e) {
                System.out.println("No response after one " + TimeUnit.MINUTES);
                futureResult.cancel(true);
                System.out.println("updateService " + updateService);
            }

        }
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
