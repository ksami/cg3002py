################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL := cmd.exe
RM := rm -rf

USER_OBJS :=

LIBS := 
PROJ := 

O_SRCS := 
C_SRCS := 
S_SRCS := 
S_UPPER_SRCS := 
OBJ_SRCS := 
ASM_SRCS := 
PREPROCESSING_SRCS := 
OBJS := 
OBJS_AS_ARGS := 
C_DEPS := 
C_DEPS_AS_ARGS := 
EXECUTABLES := 
OUTPUT_FILE_PATH :=
OUTPUT_FILE_PATH_AS_ARGS :=
AVR_APP_PATH :=$$$AVR_APP_PATH$$$
QUOTE := "
ADDITIONAL_DEPENDENCIES:=
OUTPUT_FILE_DEP:=
LIB_DEP:=

# Every subdirectory with source files must be described here
SUBDIRS := 


# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS +=  \
../delay.cpp \
../FreeRTOS2560.cpp \
../heap_1.c \
../list.c \
../microsmooth.cpp \
../port.c \
../que.cpp \
../queue.c \
../Servo.cpp \
../tasks.c \
../Ultrasonic.cpp \
../XBee.cpp


PREPROCESSING_SRCS += 


ASM_SRCS += 


OBJS +=  \
delay.o \
FreeRTOS2560.o \
heap_1.o \
list.o \
microsmooth.o \
port.o \
que.o \
queue.o \
Servo.o \
tasks.o \
Ultrasonic.o \
XBee.o

OBJS_AS_ARGS +=  \
delay.o \
FreeRTOS2560.o \
heap_1.o \
list.o \
microsmooth.o \
port.o \
que.o \
queue.o \
Servo.o \
tasks.o \
Ultrasonic.o \
XBee.o

C_DEPS +=  \
delay.d \
FreeRTOS2560.d \
heap_1.d \
list.d \
microsmooth.d \
port.d \
que.d \
queue.d \
Servo.d \
tasks.d \
Ultrasonic.d \
XBee.d

C_DEPS_AS_ARGS +=  \
delay.d \
FreeRTOS2560.d \
heap_1.d \
list.d \
microsmooth.d \
port.d \
que.d \
queue.d \
Servo.d \
tasks.d \
Ultrasonic.d \
XBee.d

OUTPUT_FILE_PATH +=FreeRTOS2560.elf

OUTPUT_FILE_PATH_AS_ARGS +=FreeRTOS2560.elf

ADDITIONAL_DEPENDENCIES:=

OUTPUT_FILE_DEP:= ./makedep.mk

LIB_DEP+= 

# AVR32/GNU C Compiler

























./%.o: .././%.c
	@echo Building file: $<
	@echo Invoking: AVR8/GNU C Compiler : 3.4.2
	$(QUOTE)C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-gcc.exe$(QUOTE)  -funsigned-char -funsigned-bitfields -DDEBUG  -I"../../../../../../../../Program Files (x86)/Arduino/hardware/arduino/cores/arduino" -I"../../../../../../../../Program Files (x86)/Arduino/hardware/arduino/variants/mega" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Demo/Common/include" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Source/include" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Source/portable/GCC/ATMega2560" -I"C:\Program Files (x86)\Arduino\hardware\arduino\cores\arduino"  -O1 -ffunction-sections -fdata-sections -fpack-struct -fshort-enums -mrelax -g2 -Wall -mmcu=atmega2560 -c -std=gnu99 -MD -MP -MF "$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)"   -o "$@" "$<"
	@echo Finished building: $<
	

./%.o: .././%.cpp
	@echo Building file: $<
	@echo Invoking: AVR8/GNU C Compiler : 3.4.2
	$(QUOTE)C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-g++.exe$(QUOTE) -funsigned-char -funsigned-bitfields -DDEBUG  -I"../../../../../../../../Program Files (x86)/Arduino/hardware/arduino/cores/arduino" -I"../../../../../../../../Program Files (x86)/Arduino/hardware/arduino/variants/mega" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Demo/Common/include" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Source/include" -I"../../../../../../Desktop/For Arduino/FreeRTOSV8.1.2/FreeRTOS/Source/portable/GCC/ATMega2560" -I"C:\Program Files (x86)\Arduino\hardware\arduino\cores\arduino"  -O1 -ffunction-sections -fdata-sections -fpack-struct -fshort-enums -mrelax -g2 -Wall -mmcu=atmega2560 -c -MD -MP -MF "$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)"   -o "$@" "$<"
	@echo Finished building: $<
	



# AVR32/GNU Preprocessing Assembler



# AVR32/GNU Assembler




ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: $(OUTPUT_FILE_PATH) $(ADDITIONAL_DEPENDENCIES)

$(OUTPUT_FILE_PATH): $(OBJS) $(USER_OBJS) $(OUTPUT_FILE_DEP) $(LIB_DEP)
	@echo Building target: $@
	@echo Invoking: AVR8/GNU Linker : 3.4.2
	$(QUOTE)C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-g++.exe$(QUOTE) -o$(OUTPUT_FILE_PATH_AS_ARGS) $(OBJS_AS_ARGS) $(USER_OBJS) $(LIBS) -Wl,-Map="FreeRTOS2560.map" -Wl,--start-group -Wl,-lm -Wl,-larduinolib  -Wl,--end-group -Wl,-L"../../../arduinolib/arduinolib/Debug"  -Wl,--gc-sections -mrelax -mmcu=atmega2560 
	@echo Finished building target: $@
	"C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-objcopy.exe" -O ihex -R .eeprom -R .fuse -R .lock -R .signature  "FreeRTOS2560.elf" "FreeRTOS2560.hex"
	"C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-objcopy.exe" -j .eeprom  --set-section-flags=.eeprom=alloc,load --change-section-lma .eeprom=0  --no-change-warnings -O ihex "FreeRTOS2560.elf" "FreeRTOS2560.eep" || exit 0
	"C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-objdump.exe" -h -S "FreeRTOS2560.elf" > "FreeRTOS2560.lss"
	"C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-objcopy.exe" -O srec -R .eeprom -R .fuse -R .lock -R .signature  "FreeRTOS2560.elf" "FreeRTOS2560.srec"
	"C:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.2.1002\avr8-gnu-toolchain\bin\avr-size.exe" "FreeRTOS2560.elf"
	
	





# Other Targets
clean:
	-$(RM) $(OBJS_AS_ARGS) $(EXECUTABLES)  
	-$(RM) $(C_DEPS_AS_ARGS)   
	rm -rf "FreeRTOS2560.elf" "FreeRTOS2560.a" "FreeRTOS2560.hex" "FreeRTOS2560.lss" "FreeRTOS2560.eep" "FreeRTOS2560.map" "FreeRTOS2560.srec"
	