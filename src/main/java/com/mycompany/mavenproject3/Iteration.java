package com.mycompany.mavenproject3;

import lombok.Data;
import lombok.experimental.Accessors;

import java.io.Serializable;

@Data
@Accessors(chain = true)
public class Iteration implements Serializable {

    private Integer varOfWork;
    private Integer capacityOfMainConveyor;
    private Integer quantityOfVagonsToSilageAtOnce;
    private Integer quantityOfVehicleDischargeStations;
    private Integer numberOfVehicleSilages;
    private Integer capacityOfVehicleSilages;
    private Integer quantityOfSilages;
    private Integer yearsModelWorking;


    public String toForeignKey(){
        return varOfWork + "-" + capacityOfMainConveyor  + "-" + quantityOfVagonsToSilageAtOnce
                + "-" + quantityOfVehicleDischargeStations  + "-" + numberOfVehicleSilages
                + "-" + capacityOfVehicleSilages  + "-" + quantityOfSilages
                + "-" + yearsModelWorking;
    }
}
