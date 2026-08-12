import xlsxwriter


def reconstruction_data():
    workbook = xlsxwriter.Workbook("Network_reconstruction_data.xlsx")
    worksheet = workbook.add_worksheet('Reconstruction Data')
    worksheet.write(0, 0, 'Network number')
    worksheet.write(0, 1, 'peak time')
    worksheet.write(0, 2, 'peak value')
    worksheet.write(0, 3, 'peak info')
    worksheet.write(0, 4, 'node name')
    worksheet.write(0, 5, 'parent name')
    worksheet.write(0, 6, 'distance from parent')
    worksheet.write(0, 7, 'branches')
    worksheet.write(0, 9, 'Input node name')
    worksheet.write(0, 10, 'parent name')
    worksheet.write(0, 11, 'distance from parent')
    worksheet.write(0, 12, 'branches')
    worksheet.write(0, 13, 'reconstruction probabilty')
    worksheet.write(0, 14, 'reconstruction time')
    worksheet.write(10, 20, 'Global result :')
    worksheet.write(10, 21, 'Global Processing time :')
    return worksheet

    # for count, reconstruction_result_node in enumerate(reconstruction_result):
    #     worksheet.write(n+count, 4, reconstruction_result_node[0])
    #     worksheet.write(n+count, 5, reconstruction_result_node[1])
    #     worksheet.write(n+count, 6, reconstruction_result_node[2])
    #     worksheet.write(n+count, 7, reconstruction_result_node[3])

    # for count, network_input_node in enumerate(nodes_input_data):
    #     worksheet.write(n+count, 9, network_input_node[0])
    #     worksheet.write(n+count, 10, network_input_node[1])
    #     worksheet.write(n+count, 11, network_input_node[2])
    #     worksheet.write(n+count, 12, network_input_node[3])

    #     # for network_peak_number in range(network_total_peak_number):
    #     #     this_peak_data = network_output[most_probable_network_number].peak_data(
    #     #         network_peak_number)
    #     #     info = network_output[most_probable_network_number].peak_information(
    #     #         this_peak_data[0])
    #     #     print(info)
    #     #     worksheet.write(n+network_peak_number, 3, info)

    # print(nodes_input_data)
    # print(loads_input_data)
    # result = verify_reconstructed_network(
    #     network_name, reconstruction_result, nodes_input_data)
    # if result == 'Successful reconstuction':
    #     worksheet.write(n+1, 0, result)
    #     final_successful_result = final_successful_result + 1
    # else:
    #     final_unsuccessful_result.append(result)
    #     worksheet.write(n+1, 0, result[0])
    # worksheet.write(n, 14, str(
    #     round((time.time() - start_time), 3))+' s')
    # worksheet.write(
    #     n, 13, str(network_output[most_probable_network_number].probability) + '  %')
    # n = n + network_total_peak_number + 1

    # print('Successefully reconstructed ', str(
    #     final_successful_result), 'out of ', str(networks_number), 'networks')
    # final_unsuccessful_result_number = len(final_unsuccessful_result)
    # worksheet.write(11, 20, 'Successefully reconstructed ' + str(
    #     final_successful_result) + ' out of ' + str(networks_number) + ' networks ')
    # worksheet.write(11, 21, str(
    #     round((time.time() - start_time_total), 3))+' seconds')
    # print('failed to reconstruct ', str(final_unsuccessful_result_number),
    #       'out of ', str(networks_number), 'networks')
    # print('Networks reconstruction total time : ', '--- %s seconds ---' %
    #       round((time.time() - start_time_total), 3))
    # if final_unsuccessful_result_number != 0:
    #     print('----------------------------------      Unsuccessfully reconstructed networks setails              ----------------------------------')
    #     for element in final_unsuccessful_result:
    #         print('\n', element[1])
    #         print(element[0])
    #         print('--->  Input data            :   ', element[2])
    #         print('\n--->  Reconstruction data   :   ', element[3])
    # workbook.close()
